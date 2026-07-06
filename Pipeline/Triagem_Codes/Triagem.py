import json, re, time
from Pipeline.ollama_local_client import chat, get_client
from Pipeline.Prompts.Triagem_Prompt import TRIAGEM_PROMPT

class TriageAnalyzer:

    def __init__(self, system_prompt_path):
        """Loads the client and the system prompt used for triage analysis."""
        self.client = get_client()
        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read().strip()

    def analyze(self, triage_text: str, patient_history: dict):
        if isinstance(patient_history, str):
            try:
                patient_history = json.loads(patient_history)
            except Exception:
                pass

        history_str = json.dumps(patient_history, indent=2, ensure_ascii=False)
        user_prompt = TRIAGEM_PROMPT.format(triagem=triage_text, data=history_str)

        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            try:
                raw_response, llm_duration, had_retry = chat(self.client, user_prompt, self.system_prompt)
                response = raw_response[0] if isinstance(raw_response, (tuple, list)) else str(raw_response)

                if "504 Server Error" in response or "Gateway Timeout" in response:
                    raise ValueError("504 Timeout detected.")

                json_data = {}
                clinical_text = response

                # The model is instructed to separate free-text analysis from the JSON payload with a [JSON_START] marker; fall back to a plain JSON search otherwise
                if "[JSON_START]" in response:
                    parts = response.split("[JSON_START]")
                    clinical_text = re.sub(r'(:|são:)\s*$', '.', parts[0].strip()).strip()
                    json_str = parts[1].strip()

                    json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
                    if not json_match:
                        raise ValueError("No valid JSON found after the tag.")
                    json_data = json.loads(json_match.group())
                else:
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if not json_match:
                        raise ValueError("Both the tag and the JSON are missing.")
                    json_data = json.loads(json_match.group())
                    clinical_text = response.replace(json_match.group(), "").strip()

                if "triagem" not in json_data:
                    raise ValueError("The JSON is missing the required 'triagem' key.")
                if "exames" not in json_data:
                    raise ValueError("The JSON is missing the required 'exames' key.")

                return clinical_text, json_data, llm_duration, (had_retry or attempt > 1)

            except Exception as e:
                print(f"[TRIAGE] Attempt {attempt}/{max_attempts} failed: {e}", flush=True)
                if attempt < max_attempts:
                    time.sleep(5)
                else:
                    print("[TRIAGE] Retry limit reached! Returning the safety fallback.", flush=True)
                    return (
                        "Não foi possível realizar a análise clínica.",
                        {"triagem": "Erro de sistema na inferência.", "exames": []},
                        0.0,True)
