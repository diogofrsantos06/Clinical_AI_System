import requests
from Pipeline.ollama_local_client import DEFAULT_BASE_URL


def parse_generation_stats(raw_ollama_response: dict) -> dict:
    """
    Extracts Ollama's own performance counters from one /api/chat response.
    All duration fields Ollama returns are in NANOSECONDS; converted here to seconds.
    """
    ns_to_s = 1e-9

    prompt_eval_count = raw_ollama_response.get("prompt_eval_count", 0)
    prompt_eval_duration = raw_ollama_response.get("prompt_eval_duration", 0) * ns_to_s
    eval_count = raw_ollama_response.get("eval_count", 0)
    eval_duration = raw_ollama_response.get("eval_duration", 0) * ns_to_s
    load_duration = raw_ollama_response.get("load_duration", 0) * ns_to_s
    total_duration = raw_ollama_response.get("total_duration", 0) * ns_to_s

    return {
        "model_load_seconds": load_duration,
        "prompt_tokens": prompt_eval_count,
        "prompt_processing_seconds": prompt_eval_duration,
        "prompt_tokens_per_second": (prompt_eval_count / prompt_eval_duration) if prompt_eval_duration > 0 else 0.0,
        "generated_tokens": eval_count,
        "generation_seconds": eval_duration,
        "generation_tokens_per_second": (eval_count / eval_duration) if eval_duration > 0 else 0.0,
        "total_seconds_reported_by_ollama": total_duration,
    }


def get_loaded_models(client: dict = None) -> list:
    """
    Calls GET /api/ps on the Ollama server: which model(s) are currently loaded
    into memory, how much RAM/VRAM each is using right now, and when they'll be
    auto-unloaded (keep_alive countdown).
    """
    base_url = client["base_url"] if client else DEFAULT_BASE_URL
    response = requests.get(f"{base_url}/api/ps", timeout=10)
    response.raise_for_status()
    data = response.json()

    models = []
    for m in data.get("models", []):
        models.append({
            "name": m.get("name"),
            "size_ram_gb": round(m.get("size", 0) / (1024 ** 3), 2),
            "size_vram_gb": round(m.get("size_vram", 0) / (1024 ** 3), 2),
            "fully_loaded_in_gpu": m.get("size_vram", 0) >= m.get("size", 0),
            "expires_at": m.get("expires_at"),
        })
    return models


def get_server_version(client: dict = None) -> str:
    """Quick health-check / version info for the Ollama server."""
    base_url = client["base_url"] if client else DEFAULT_BASE_URL
    response = requests.get(f"{base_url}/api/version", timeout=10)
    response.raise_for_status()
    return response.json().get("version", "desconhecida")


def get_model_details(model: str, client: dict = None) -> dict:
    """
    Calls POST /api/show for one model: exact quantization, parameter count,
    context window size, and the full Modelfile/template in use.
    """
    base_url = client["base_url"] if client else DEFAULT_BASE_URL
    response = requests.post(f"{base_url}/api/show", json={"name": model}, timeout=10)
    response.raise_for_status()
    data = response.json()

    details = data.get("details", {})
    model_info = data.get("model_info", {})

    # The context-length key is namespaced per model family (e.g. "gemma3.context_length")
    context_length = next((v for k, v in model_info.items() if k.endswith("context_length")), None)

    return {
        "parameter_size": details.get("parameter_size"),
        "quantization_level": details.get("quantization_level"),
        "family": details.get("family"),
        "context_length": context_length,
        "template": data.get("template"),
    }