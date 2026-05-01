import requests

DEFAULT_BASE_URL = "http://172.30.2.225:11434"
DEFAULT_MODEL = "llama3.3:70b-instruct-q4_K_M"  # "gemma3:27b"

def get_client(base_url: str = DEFAULT_BASE_URL):
    """Inicializa o cliente com o URL do servidor local."""
    return {
        "base_url": base_url
    }

def chat(client, user_prompt, system_prompt=None, model=DEFAULT_MODEL):
    """Envia um pedido de chat para a API do Ollama e devolve a resposta."""
    url = f"{client['base_url']}/api/chat"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    messages.append({"role": "user", "content": user_prompt})

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.0,  # Zero para garantir respostas diretas
            "top_p": 1.0,
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Erro ao chamar a API: {str(e)}"

# --- Teste de Ligação ---
if __name__ == "__main__":
    cliente_local = get_client()
    
    print(f"A testar ligação ao servidor {cliente_local['base_url']}...")
    print(f"A usar o modelo: {DEFAULT_MODEL}\n")
    
    resposta_teste = chat(
        client=cliente_local,
        user_prompt="Responde apenas com a frase: 'Ligação estabelecida com sucesso e a correr localmente!'. Não adiciones mais nenhum texto.",
        system_prompt="És um assistente de testes de sistema."
    )
    
    print("--- RESULTADO ---")
    print(resposta_teste)