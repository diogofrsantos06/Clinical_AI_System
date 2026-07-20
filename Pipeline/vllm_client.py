import time
import uuid
import requests

DEFAULT_BASE_URL = "https://172.30.2.225:8000"
DEFAULT_MODEL = "qwen3.6-35b-a3b"  # ajusta para o nome exato devolvido por /v1/models

# O servidor usa um certificado autoassinado (confirmado no exemplo do orientador,
# que também desativa a validação). Se um dia houver um certificado válido, muda para True.
VERIFY_TLS = False


def get_client(base_url: str = DEFAULT_BASE_URL) -> dict:
    """Wraps the vLLM server URL in a simple client dict (same shape as the Ollama client)."""
    return {"base_url": base_url}


def chat(client: dict, user_prompt: str, system_prompt: str = None, model: str = DEFAULT_MODEL,
         retries: int = 20, retry_delay: float = 1.0, keep_alive: int = -1, stats_sink: dict = None) -> tuple:
    """
    Sends a single, non-streaming chat request to vLLM's OpenAI-compatible API.
    Same signature and return shape as ollama_local_client.chat(), so no other file
    in the pipeline needs to change to use this instead.

    'keep_alive' is accepted but ignored: vLLM loads the model once when the server
    process starts and keeps it loaded for as long as the process is alive — there's
    no per-request load/unload like Ollama's.
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.0,
        "top_p": 1.0,
        # Required: Qwen3 supports a "thinking" mode that wraps a visible reasoning
        # block in <think>...</think> before the actual answer. Gemma/Ollama never
        # did this, and this pipeline expects a clean JSON response — so thinking
        # must stay explicitly off, not left to whatever the server defaults to.
        "chat_template_kwargs": {"enable_thinking": False},
        # max_tokens is intentionally NOT set: vLLM's own default when it's omitted
        # is "context window minus prompt size", which matches the old behaviour
        # (Ollama's num_ctx bounded the whole exchange, with no separate output cap).
    }

    url = f"{client['base_url']}/v1/chat/completions"
    session_id = str(uuid.uuid4())
    headers = {
        "Content-Type": "application/json",
        "X-Request-ID": session_id,
    }

    is_retry = False

    for attempt in range(1, retries + 1):
        try:
            start_inference = time.perf_counter()
            response = requests.post(url, json=payload, headers=headers, timeout=None, verify=VERIFY_TLS)

            if response.status_code == 200:
                duration = time.perf_counter() - start_inference
                data = response.json()
                content = data["choices"][0]["message"]["content"]

                if stats_sink is not None:
                    usage = data.get("usage") or {}
                    completion_tokens = usage.get("completion_tokens", 0)
                    stats_sink.update({
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "generated_tokens": completion_tokens,
                        # Wall-clock based (network + inference): vLLM's usage block,
                        # unlike Ollama's response, doesn't include the server's own
                        # generation-only duration, so this is the closest available.
                        "generation_tokens_per_second": (completion_tokens / duration) if duration > 0 else 0.0,
                        # Not available through this API: no equivalent to Ollama's /api/ps.
                        "model_ram_gb": None,
                        "model_vram_gb": None,
                    })

                return content, duration, is_retry

            # vLLM returns 503 when the request queue is full / server is busy
            if response.status_code == 503:
                is_retry = True
                if attempt < retries:
                    print(f"[{session_id}] 503 - waiting {retry_delay:.0f}s before retrying...")
                    time.sleep(retry_delay)
                    continue
                return f"Error: 503 after {retries} attempts", 0.0, is_retry

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
    """
    No-op for vLLM: the model is loaded once when the server process starts and
    stays loaded. Kept under this name only so code written for Ollama
    (extraction_service.py, patient_summary_service.py, triage_service.py, views.py)
    keeps working unchanged when switching providers.
    """
    return True


def ollama_unload(client: dict, model: str = DEFAULT_MODEL) -> bool:
    """No-op for vLLM — see ollama_warmup() above for why."""
    return True
