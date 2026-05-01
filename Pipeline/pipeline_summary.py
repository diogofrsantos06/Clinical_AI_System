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

    def run_summary(self, list_of_extractions: list) -> str:
        """
        Entrada: Lista de DIÁRIOS EXTRAÍDOS (JSON) vindos da BD.
        Saída: Texto do sumário final.
        """
        try:
            structured_payload = {}
            
            # Usamos enumerate para ter um contador (i) que começa no 1
            for i, item in enumerate(list_of_extractions, start=1):
                # Cria uma chave única juntando o título e o número do registo
                diary_label = f"{item['titulo']} (Registo {i})" 
                
                structured_payload[diary_label] = item["dados"]

            print("Esta é do STRUCTURED_PAYLOAD: ")
            print(json.dumps(structured_payload, indent=2, ensure_ascii=False)) # Imprime bonito para conseguires ler

            summary_text = self.summarizer.generate_summary(structured_payload)

            if not summary_text or "Error code:" in str(summary_text) or "limit" in str(summary_text).lower():
                print(f"[Pipeline] IA devolveu um erro em vez de resumo: {summary_text}")
                return None 

            return summary_text

        except Exception as e:
            print(f"[Pipeline] Erro crítico na geração: {str(e)}")
            return None