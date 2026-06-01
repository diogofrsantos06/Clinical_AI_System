PROVIDER = "groq"

if PROVIDER == "ollama":
    from Pipeline.ollama_local_client import get_client, chat
elif PROVIDER == "groq":
    from Pipeline.groq_client import get_client, chat
else:
    raise ValueError(f"Provider desconhecido: {PROVIDER}")