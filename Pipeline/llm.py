#PROVIDER = "vllm"  # "ollama" or "vllm"
PROVIDER = "groq"

if PROVIDER == "ollama":
    from Pipeline.ollama_local_client import get_client, chat, ollama_warmup, ollama_unload
elif PROVIDER == "vllm":
    from Pipeline.vllm_client import get_client, chat, ollama_warmup, ollama_unload
elif PROVIDER == "groq":
    from Pipeline.Synthetic_Data.openai_client import get_client, chat, ollama_unload, ollama_warmup
else:
    raise ValueError(f"Unknown provider: {PROVIDER}")