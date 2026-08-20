"""
Cliente para a API da OpenAI (modelo GPT-5.6 Terra), usado como alternativa ao
groq_client.py para a geração de dados sintéticos. Ficheiro completamente
independente — não interfere com o cliente da Groq.

Requer a variável de ambiente OPENAI_API_KEY definida.
"""
import os
import time
import requests

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-5.6-terra"


def get_client():
    """Devolve a chave da API, lida do ambiente. Lança erro claro se não estiver definida."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "A variável de ambiente OPENAI_API_KEY não está definida. "
            "Define-a antes de correres qualquer geração sintética."
        )
    return api_key


def chat(client, user_prompt, system_prompt, model=DEFAULT_MODEL,
         temperature=1, max_tokens=4000, max_attempts=3, stats_sink=None):
    """
    Faz uma chamada de chat à OpenAI. 'client' é a chave da API (string), devolvida
    por get_client() — o nome do parâmetro é 'client' (não 'api_key') para bater
    certo com o resto do pipeline (pdf_splitter.py chama chat(client=..., ...)).
    temperature=0.9 por omissão (mais alto que o resto do projeto) porque aqui
    queremos variedade entre pacientes sintéticos, não determinismo. max_tokens
    definido explicitamente — sem isto, corre-se o risco de a resposta ser cortada
    por um valor por omissão baixo (já vimos este problema com a Groq).
    """
    headers = {
        "Authorization": f"Bearer {client}",
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
            response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=90)
            duration = time.perf_counter() - start

            if response.status_code != 200:
                raise ValueError(f"OpenAI API error {response.status_code}: {response.text[:300]}")

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})

            if stats_sink is not None:
                stats_sink["prompt_tokens"] = usage.get("prompt_tokens")
                stats_sink["completion_tokens"] = usage.get("completion_tokens")
                stats_sink["duration"] = duration
                stats_sink["attempt_count"] = attempt

            # O resto do pipeline (extraction.py, Summarization.py, Triagem.py) espera
            # sempre um triplo (resposta, duração, houve_retry) — nunca só a string.
            had_retry = (attempt > 1)
            return content, duration, had_retry

        except Exception as e:
            last_error = e
            print(f"[OPENAI] Attempt {attempt}/{max_attempts} failed: {e}", flush=True)
            if attempt < max_attempts:
                time.sleep(3)

    raise RuntimeError(f"OpenAI call failed after {max_attempts} attempts: {last_error}")


def ollama_warmup(client: str, model: str = DEFAULT_MODEL) -> bool:
    """
    No-op para a API da OpenAI: não há modelo a "carregar" localmente, o pedido
    vai direto para o servidor deles. Mantido com este nome só para o código
    escrito a pensar no Ollama (extraction_service.py, patient_summary_service.py,
    triage_service.py, views.py) continuar a funcionar sem alterações ao trocar
    de fornecedor.
    """
    return True


def ollama_unload(client: str, model: str = DEFAULT_MODEL) -> bool:
    """No-op para a API da OpenAI — ver ollama_warmup() acima para o porquê."""
    return True