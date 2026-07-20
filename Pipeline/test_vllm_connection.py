"""
Teste isolado de ligação ao vLLM. Corre com:
    PYTHONPATH=/caminho/para/Clinical_AI_System python3 Pipeline/test_vllm_connection.py

Não mexe em Django nem no resto do pipeline — só confirma que o vllm_client.py
consegue mesmo falar com o servidor.
"""
from Pipeline.vllm_client import get_client, chat

client = get_client()

print(f"A ligar a {client['base_url']}...")

texto, duracao, houve_retry = chat(
    client,
    user_prompt="Diz olá numa frase curta.",
    system_prompt="Responde sempre em português europeu.",
)

print()
print("Resposta:", texto)
print(f"Demorou: {duracao:.2f}s")
print(f"Houve retry: {houve_retry}")
