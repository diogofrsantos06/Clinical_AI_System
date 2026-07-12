import time, uuid, requests

#DEFAULT_BASE_URL = "http://172.30.2.225:11434" 
DEFAULT_BASE_URL = "http://172.30.2.225:8000/v1"
#DEFAULT_MODEL = "gemma3:27b" 
#DEFAULT_MODEL = "qwen2.5:14b-instruct" 
DEFAULT_MODEL = "qwen3:14b-q4_K_M"  

CONTEXT_WINDOW = 32768

def get_client(base_url: str = DEFAULT_BASE_URL) -> dict:
    """Wraps the Ollama server URL in a simple client dict."""
    return {"base_url": base_url}

def chat(client: dict, user_prompt: str, system_prompt: str = None, model: str = DEFAULT_MODEL, 
         retries: int = 5, retry_delay: float = 2.0) -> tuple:
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    # Payload simplificado para formato OpenAI/vLLM
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 4096 # O vLLM usa max_tokens em vez de num_ctx
    }

    # O endpoint no vLLM é /chat/completions
    url = f"{client['base_url']}/chat/completions"
    
    # Se te deram uma API KEY, usa-a aqui. Se não deram, tenta sem o header Authorization
    headers = {
        "Authorization": "Bearer vllm_ulsc_d66bdbbe68f4af13a90936bed53adfad0ded77a2", # Insere aqui a chave que recebeste
        "Content-Type": "application/json"
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=None)
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return content, 0.0, False # Ajustar o cálculo do tempo se necessário

            if response.status_code in [429, 503]: # vLLM usa 429 para rate limit
                time.sleep(retry_delay)
                continue
                
            response.raise_for_status()
            
        except Exception as e:
            if attempt == retries: return f"Error: {str(e)}", 0.0, True
            time.sleep(retry_delay)

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
