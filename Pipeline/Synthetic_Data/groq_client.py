"""
Cliente para a API da Groq, usada apenas para geração de dados sintéticos
(sementes de pacientes, percursos clínicos, e futuramente conteúdo de diários).

Requer a variável de ambiente GROQ_API_KEY definida.
"""
import os
import time
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.3-70b-versatile" # "llama-3.1-8b-instant"  # ajusta ao modelo Groq que quiseres usar


def get_client():
    """Devolve a chave da API, lida do ambiente. Lança erro claro se não estiver definida."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "A variável de ambiente GROQ_API_KEY não está definida. "
            "Define-a antes de correres qualquer geração sintética."
        )
    return api_key


def chat(api_key, user_prompt, system_prompt, model=DEFAULT_MODEL,
         temperature=0.9, max_tokens=4000, max_attempts=3, stats_sink=None):
    """
    Faz uma chamada de chat à Groq. temperature=0.9 por omissão (mais alto que o
    resto do projeto) porque aqui queremos variedade entre pacientes sintéticos,
    não determinismo.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "temperature": temperature,
        "max_completion_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            start = time.perf_counter()
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
            duration = time.perf_counter() - start

            if response.status_code != 200:
                raise ValueError(f"Groq API error {response.status_code}: {response.text[:300]}")

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})

            if stats_sink is not None:
                stats_sink["prompt_tokens"] = usage.get("prompt_tokens")
                stats_sink["completion_tokens"] = usage.get("completion_tokens")
                stats_sink["duration"] = duration
                stats_sink["attempt_count"] = attempt

            had_retry = (attempt > 1)
            return content, duration, had_retry

        except Exception as e:
            last_error = e
            print(f"[GROQ] Attempt {attempt}/{max_attempts} failed: {e}", flush=True)
            if attempt < max_attempts:
                time.sleep(20)

    raise RuntimeError(f"Groq call failed after {max_attempts} attempts: {last_error}")

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

