from pathlib import Path
from Pipeline.Triagem_Codes.Triagem import TriageAnalyzer

BASE_DIR = Path(__file__).resolve().parent.parent
TRIAGE_SYSTEM_PROMPT_PATH = BASE_DIR / "Pipeline" / "System_Prompts" / "Triagem.txt"

class TriagePipeline:
    def __init__(self):
        self.analyzer = TriageAnalyzer(system_prompt_path=TRIAGE_SYSTEM_PROMPT_PATH)

    def run(self, triage_text: str, patient_history: dict):
        """
        Runs the triage analyzer and returns the API-facing dict.
        """
        try:
            result = self.analyzer.analyze(triage_text, patient_history)

            if not isinstance(result, tuple) or len(result) < 8:
                print(f"[TRIAGE PIPELINE] Unexpected return from the analyzer: {result}", flush=True)
                return {"error": "Invalid return format from the analyzer"}

            clinical_text, structured_data, llm_duration, had_retry, tokens_per_second, model_ram_gb, model_vram_gb, extra_stats = result

            if 'triagem' not in structured_data:
                print(f"[TRIAGE PIPELINE] WARNING - 'triagem' key not found in: {structured_data}", flush=True)

            return {
                "analise_texto": clinical_text,
                "dados_estruturados": structured_data,
                "tempo_llm": llm_duration,
                "houve_retry": had_retry,
                "tokens_per_second": tokens_per_second,
                "model_ram_gb": model_ram_gb,
                "model_vram_gb": model_vram_gb,
                **extra_stats
            }

        except Exception as e:
            print(f"[TRIAGE PIPELINE] Critical error: {str(e)}", flush=True)
            return {"error": str(e), "analise_texto": "", "dados_estruturados": {}}
