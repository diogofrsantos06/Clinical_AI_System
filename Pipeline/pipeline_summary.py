import sys
from pathlib import Path

from Pipeline.Summary_Codes.Summarization import Summarizer

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
SUMMARY_SYSTEM_PROMPT_PATH = BASE_DIR / "Pipeline" / "System_Prompts" / "Summary.txt"


class SummaryPipeline:
    def __init__(self, client=None):
        self.summarizer = Summarizer(system_prompt_path=SUMMARY_SYSTEM_PROMPT_PATH)

    def run_summary(self, list_of_extractions: list) -> tuple:
        """
        Entrada: Lista de DIÁRIOS EXTRAÍDOS (JSON) vindos da BD.
        Saída: Tuplo (summary_text, tempo_llm, houve_retry) para o serviço do Django.
        """
        try:
            structured_payload = {}
            
            for i, item in enumerate(list_of_extractions, start=1):

                diary_label = f"{item['titulo']} (Registo {i})" 
                
                structured_payload[diary_label] = item["dados"]

            # Executa a chamada ao summarizer (que agora corre as 4 fases internamente)
            summary_text, tempos_seccoes, houve_retry = self.summarizer.generate_summary(structured_payload)

            # Validação de segurança para tratamento de erros da API da Groq/Ollama
            if not summary_text or "Error code:" in str(summary_text) or "limit" in str(summary_text).lower():
                return None, 0.0, False

            return summary_text, tempos_seccoes, houve_retry

        except Exception as e:
            print(f"[Pipeline] Erro crítico na geração: {str(e)}")
            return None, 0.0, False