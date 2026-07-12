import json, re, time
from typing import Dict, Any

from Pipeline.ollama_local_client import chat, get_client
from Pipeline.Prompts.Extraction_Prompt import get_prompt_for_diary_extraction

LIST_FIELDS = ["diagnosticos", "medicacao", "alergias", "exames", "sintomas", "plano"]

class DiaryExtractor:
    def __init__(self, system_prompt_path):
        """Loads the client and the system prompt used for every extraction call."""        
        self.client = get_client()

        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read().strip()
    
    def clean_json_response(self, response: str) -> str:
        """Strips markdown fences and pulls out the first valid JSON object in the response."""
        if not response:
            raise ValueError("Empty response from the LLM")

        text = response.strip()

        text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
        text = re.sub(r"```", "", text)

        # Fast path: the response is already valid JSON as-is
        try:
            json.loads(text)
            return text
        except:
            pass

        # Fallback: extract the first {...} block even if there's extra text around it
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            candidate = match.group(0)
            try:
                return json.dumps(json.loads(candidate))
            except Exception:
                pass

        print(f"[EXTRACTION] Could not parse a valid JSON object from the LLM response ({len(response)} chars).", flush=True)

        raise ValueError("Invalid JSON")
    

    def extract_full_diary(self, diary_text: str) -> Dict[str, Any]:
        """Extracts one diary into structured JSON, retrying up to 3 times on failure (e.g. 504 timeout)."""
        user_prompt = get_prompt_for_diary_extraction(diary_text)
        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            try:
                stats = {}
                response, llm_duration, had_retry = chat(self.client, user_prompt, self.system_prompt, stats_sink=stats)

                json_str = self.clean_json_response(response)
                data = json.loads(json_str)

                if not isinstance(data, dict):
                    raise ValueError("The LLM response is not a valid JSON object.")

                for field in LIST_FIELDS:
                    if field in data and not isinstance(data[field], list):
                        raise ValueError(f"Broken format: section '{field}' should be a list, got {type(data[field]).__name__}.")

                return {
                    "data": data,
                    "llm_duration": llm_duration,
                    "had_retry": had_retry or (attempt > 1),
                    "tokens_per_second": stats.get("generation_tokens_per_second", 0.0),
                    "model_ram_gb": stats.get("model_ram_gb"),
                    "model_vram_gb": stats.get("model_vram_gb"),
                    "status": "success"
                }

            except Exception as e:
                print(f"[EXTRACTION] Attempt {attempt}/{max_attempts} failed: {str(e)}", flush=True)

                if attempt < max_attempts:
                    print("[EXTRACTION] Waiting 5 seconds to let the server cool down before retrying...", flush=True)
                    time.sleep(5)
                else:
                    print("[EXTRACTION] Retry limit reached! Creating an empty record to avoid blocking the pipeline.", flush=True)

                    return {
                        "data": {},
                        "llm_duration": 0.0,
                        "had_retry": True,
                        "status": "success",  # kept as "success" on purpose: this is a graceful-degradation path, not a pipeline error, see 'extraction_failed' below
                        "extraction_failed": True
                    }
