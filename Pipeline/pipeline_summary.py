import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
SUMMARY_SYSTEM_PROMPT_PATH = BASE_DIR / "Pipeline" / "System_Prompts" / "Summary.txt"

from Pipeline.Summary_Codes.Summarization import Summarizer

class SummaryPipeline:
    def __init__(self):
        self.summarizer = Summarizer(system_prompt_path=SUMMARY_SYSTEM_PROMPT_PATH)

    def run_summary(self, list_of_extractions: list) -> tuple:
        """
        Entrada: Lista de DIÁRIOS EXTRAÍDOS (JSON) vindos da BD.
        Saída: Texto do sumário final.
        """
        try:
            structured_payload = {}
            
            for i, item in enumerate(list_of_extractions, start=1):

                diary_label = f"{item['titulo']} (Registo {i})" 
                
                structured_payload[diary_label] = item["dados"]

            result = self.summarizer.generate_summary(structured_payload)

            if isinstance(result, str): 
                return result, 0.0, False

            summary_text, tempo_llm, houve_retry = result

            # Validação de erros
            if not summary_text or "Error code:" in str(summary_text) or "limit" in str(summary_text).lower():
                return None, 0.0, False

            # Mudança 3: Passamos o tuplo completo para o serviço
            return summary_text, tempo_llm, houve_retry

        except Exception as e:
            print(f"[Pipeline] Erro crítico na geração: {str(e)}")
            return None, 0.0, False