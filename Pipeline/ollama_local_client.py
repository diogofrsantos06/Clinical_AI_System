import time
import uuid
import requests

DEFAULT_BASE_URL = "http://172.30.2.225:11434" 
#DEFAULT_MODEL = "gemma3:27b" 
#DEFAULT_MODEL = "qwen2.5:14b-instruct" 
DEFAULT_MODEL = "qwen3:14b-q4_K_M"  #qwen2.5:0.5b



def get_client(base_url: str = DEFAULT_BASE_URL) -> dict:
    """Inicializa o cliente com o URL do servidor local."""
    return {"base_url": base_url}


def chat(client: dict,user_prompt: str,system_prompt: str = None,model: str = DEFAULT_MODEL,retries: int = 20,retry_delay: float = 1.0,) -> tuple:
    
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

    is_retry = False

    for attempt in range(1, retries + 1):
        wait = retry_delay  

        try:
            with requests.Session() as session:
                start_inference = time.perf_counter()

                response = session.post(url, json=payload, timeout=1800)

                if response.status_code == 200:
                    duration = time.perf_counter() - start_inference
                    data = response.json()
                    return data["message"]["content"], duration, is_retry

                if response.status_code in [404, 503]:
                    is_retry = True 
                    if attempt < retries:
                        print(f"[{session_id}] {response.status_code} — Aguarda {wait:.0f}s...")
                        time.sleep(wait)
                        continue
                    return f"Erro: {response.status_code} após {retries} tentativas", 0.0, is_retry

                response.raise_for_status()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            is_retry = True
            if attempt < retries:
                print(f"[{session_id}] Erro de rede, aguarda {wait:.0f}s...")
                time.sleep(wait)
                continue
                    
            return f"Erro: {str(e)}", 0.0, is_retry

        except requests.exceptions.RequestException as e:
            return f"Erro: {str(e)}", 0.0, is_retry

        return "Erro: Limite de tentativas", 0.0, is_retry
    

def ollama_warmup(client: dict, model: str = DEFAULT_MODEL) -> bool:
    """
    CHAMADA ZERO: Força o Ollama a carregar o modelo para a memória RAM/VRAM
    utilizando a rota /api/chat (evitando bloqueios de proxy 404).
    """
    url = f"{client['base_url']}/api/chat"
    payload = {
        "model": model,
        "messages": [],  # Lista vazia força o Ollama apenas a carregar o modelo
        "keep_alive": -1 # Fica permanente até mandarmos parar
    }
    try:
        print(f"[Ollama] Ativando Chamada Zero para o modelo '{model}' via /api/chat...", flush=True)
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            print(f"[Ollama] Modelo '{model}' carregado na memória e pronto para as Threads!", flush=True)
            return True
        print(f"[Ollama] Resposta inesperada no aquecimento: {response.status_code}", flush=True)
    except Exception as e:
        print(f"[Ollama] Falha ao executar a Chamada Zero: {e}", flush=True)
    return False


def ollama_unload(client: dict, model: str = DEFAULT_MODEL) -> bool:
    """
    MANDAR PARAR: Força o Ollama a descarregar o modelo da memória RAM/VRAM
    utilizando a rota /api/chat (keep_alive = 0).
    """
    url = f"{client['base_url']}/api/chat"
    payload = {
        "model": model,
        "messages": [],
        "keep_alive": 0  # 0 descarrega o modelo imediatamente
    }
    try:
        print(f"[Ollama] Ativando 'Mandar Parar' via /api/chat para libertar o servidor...", flush=True)
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"[Ollama] Modelo '{model}' removido da memória com sucesso.", flush=True)
            return True
    except Exception as e:
        print(f"[Ollama] Erro ao descarregar o modelo: {e}", flush=True)
    return False