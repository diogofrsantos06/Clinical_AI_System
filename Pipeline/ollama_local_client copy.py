import time, uuid, requests

DEFAULT_BASE_URL = "http://172.30.2.225:11434" 
#DEFAULT_MODEL = "gemma3:27b" 
#DEFAULT_MODEL = "qwen2.5:14b-instruct" 
DEFAULT_MODEL = "qwen3:14b-q4_K_M"  

CONTEXT_WINDOW = 32768

def get_client(base_url: str = DEFAULT_BASE_URL) -> dict:
    """Wraps the Ollama server URL in a simple client dict."""
    return {"base_url": base_url}

def chat(client: dict, user_prompt: str, system_prompt: str = None, model: str = DEFAULT_MODEL,
         retries: int = 20, retry_delay: float = 1.0, keep_alive: int = -1, stats_sink: dict = None) -> tuple:
    """Sends a chat request to Ollama, retrying on 404/503/network errors."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "keep_alive": keep_alive,
        "options": {
            "temperature": 0.0,
            "top_p": 1.0,
            "num_ctx": CONTEXT_WINDOW,
        },
    }

    url = f"{client['base_url']}/api/chat"
    session_id = str(uuid.uuid4())

    headers = {
        "Connection": "close",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "X-Session-ID": session_id,
        "X-Request-ID": session_id
    }

    is_retry = False

    for attempt in range(1, retries + 1):
        try:
            with requests.Session() as session:
                start_inference = time.perf_counter()

                response = session.post(url, json=payload, headers=headers, timeout=None)

                if response.status_code == 200:
                    duration = time.perf_counter() - start_inference
                    data = response.json()
                    
                    if stats_sink is not None:
                        from Pipeline.ollama_stats import parse_generation_stats, get_loaded_models
                        stats_sink.update(parse_generation_stats(data))
                        try:
                            loaded = get_loaded_models(client)
                            match = next((m for m in loaded if m["name"] == model), None)
                            if match:
                                stats_sink["model_ram_gb"] = match["size_ram_gb"]
                                stats_sink["model_vram_gb"] = match["size_vram_gb"]
                        except Exception:
                            pass  # don't fail the whole call just because this extra lookup failed

                    return data["message"]["content"], duration, is_retry

                # Ollama returns 404 right after loading a new model into memory, and 503 when busy
                if response.status_code in [404, 503]:
                    is_retry = True
                    if attempt < retries:
                        print(f"[{session_id}] {response.status_code} - waiting {retry_delay:.0f}s before retrying...")
                        time.sleep(retry_delay)
                        continue
                    return f"Error: {response.status_code} after {retries} attempts", 0.0, is_retry

                response.raise_for_status()

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            is_retry = True
            if attempt < retries:
                print(f"[{session_id}] Network error, waiting {retry_delay:.0f}s before retrying...")
                time.sleep(retry_delay)
                continue

            return f"Error: {str(e)}", 0.0, is_retry

        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}", 0.0, is_retry


def ollama_warmup(client: dict, model: str = DEFAULT_MODEL) -> bool:
    """Sends a throwaway 1-token request so the model is already loaded when real work arrives."""
    url = f"{client['base_url']}/api/chat"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Hi"}],
        "keep_alive": -1,
        "options": {
            "num_predict": 1,
            "num_ctx": CONTEXT_WINDOW,
        }
    }
    headers = {
        "Connection": "close",
        "Cache-Control": "no-cache"
    }
    try:
        print(f"[Ollama] Warming up model '{model}'...", flush=True)
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        return response.status_code == 200
    except Exception as e:
        print(f"[Ollama] Warmup failed: {e}", flush=True)
    return False


def ollama_unload(client: dict, model: str = DEFAULT_MODEL) -> bool:
    """Forces Ollama to unload the model from RAM/VRAM (keep_alive=0) to free the shared server."""
    url = f"{client['base_url']}/api/chat"
    payload = {
        "model": model,
        "messages": [],
        "keep_alive": 0
    }
    try:
        print("[Ollama] Requesting model unload to free up the server...", flush=True)
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"[Ollama] Model '{model}' unloaded successfully.", flush=True)
            return True
    except Exception as e:
        print(f"[Ollama] Error unloading model: {e}", flush=True)
    return False
