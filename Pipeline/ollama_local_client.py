import time
import uuid
import requests

DEFAULT_BASE_URL = "http://172.30.2.225:11434"
DEFAULT_MODEL = "gemma3:27b"


def get_client(base_url: str = DEFAULT_BASE_URL) -> dict:
    """Inicializa o cliente com o URL do servidor local."""
    return {"base_url": base_url}


def chat(client: dict,
    user_prompt: str,
    system_prompt: str = None,
    model: str = DEFAULT_MODEL,
    retries: int = 10,
    retry_delay: float = 10.0,
) -> str:
    """
    Envia um pedido de chat para a API do Ollama.

    - Sessão HTTP isolada por tentativa (sem partilha de estado).
    - Backoff exponencial em caso de 404, 503, timeout ou erro de ligação:
        tentativa 1 → espera 15s
        tentativa 2 → espera 30s
    - Erros irrecuperáveis (ex: 400 bad request) falham imediatamente sem retry.
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.0,
            "top_p": 1.0,
        },
    }

    url = f"{client['base_url']}/api/chat"
    session_id = str(uuid.uuid4())

    for attempt in range(1, retries + 1):
        wait = retry_delay  

        try:
            with requests.Session() as session:
                response = session.post(url, json=payload, timeout=1800)

                if response.status_code == 404:
                    if attempt < retries:
                        print(f"[{session_id}] 404 — modelo a carregar "
                              f"(tentativa {attempt}/{retries}), aguarda {wait:.0f}s...")
                        time.sleep(wait)
                        continue
                    return f"Erro ao chamar a API: 404 após {retries} tentativas"

                if response.status_code == 503:
                    if attempt < retries:
                        print(f"[{session_id}] 503 — servidor sobrecarregado "
                              f"(tentativa {attempt}/{retries}), aguarda {wait:.0f}s...")
                        time.sleep(wait)
                        continue
                    return f"Erro ao chamar a API: 503 após {retries} tentativas"

                response.raise_for_status()
                data = response.json()
                return data["message"]["content"]

        except requests.exceptions.ConnectionError as e:
            if attempt < retries:
                print(f"[{session_id}] Erro de ligação (tentativa {attempt}/{retries}), "
                      f"aguarda {wait:.0f}s...")
                time.sleep(wait)
            else:
                return f"Erro ao chamar a API: {str(e)}"

        except requests.exceptions.Timeout:
            if attempt < retries:
                print(f"[{session_id}] Timeout (tentativa {attempt}/{retries}), "
                      f"aguarda {wait:.0f}s...")
                time.sleep(wait)
            else:
                return f"Erro ao chamar a API: timeout após {retries} tentativas"

        except requests.exceptions.RequestException as e:
            # Erros irrecuperáveis (400, etc.) — falha imediata sem retry
            return f"Erro ao chamar a API: {str(e)}"

    return f"Erro ao chamar a API: falhou após {retries} tentativas"

