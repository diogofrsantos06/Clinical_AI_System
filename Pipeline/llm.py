PROVIDER = "vllm"  # "ollama" or "vllm"

if PROVIDER == "ollama":
    from Pipeline.ollama_local_client import get_client, chat, ollama_warmup, ollama_unload
elif PROVIDER == "vllm":
    from Pipeline.vllm_client import get_client, chat, ollama_warmup, ollama_unload
else:
    raise ValueError(f"Unknown provider: {PROVIDER}")