PROVIDER = "ollama"

if PROVIDER == "ollama":
    from Pipeline.ollama_local_client import get_client, chat, ollama_warmup, ollama_unload
elif PROVIDER == "groq":
    from Pipeline.groq_client import get_client, chat
    def ollama_warmup(client, model=None): pass
    def ollama_unload(client, model=None): pass
else:
    raise ValueError(f"Provider desconhecido: {PROVIDER}")