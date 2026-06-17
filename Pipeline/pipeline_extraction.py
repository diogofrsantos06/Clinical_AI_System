import sys
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent 
sys.path.append(str(BASE_DIR))

from Pipeline.Extraction_Codes.extraction import DiaryExtractor
from Pipeline.Extraction_Codes.diary_cleaner import DiaryCleaner

class ExtractionPipeline:
    def __init__(self):

        self.extraction_prompt = BASE_DIR / "Pipeline" / "System_Prompts" / "Extraction.txt"
        
        self.cleaner = DiaryCleaner()
        self.extractor = DiaryExtractor(self.extraction_prompt)

    def run(self, raw_diary_text: str) -> Dict[str, Any]:
        try:
            clean_text = self.cleaner.clean_diary(raw_diary_text)

            extraction_result = self.extractor.extract_full_diary(clean_text)

            if "erro" in extraction_result:
                return {"status": "error", "message": "Falha na extração"}

            return {
                "status": "success",
                "cleaned_text": clean_text,
                "extracted_data": extraction_result.get("dados",[]), 
                "tempo_llm": extraction_result.get("tempo_llm", 0.0), 
                "houve_retry": extraction_result.get("houve_retry", False)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro no processamento do pipeline: {str(e)}"
            }
    def run_parallel(self, list_of_diaries: list) -> list:
        """
        Recebe a lista de diários da segmentação: [{"titulo": "...", "texto": "..."}].
        Limpa o texto localmente de cada um e aciona o extrator multi-thread.
        """
        try:
            diarios_pre_limpos = []
            for item in list_of_diaries:
                # Limpeza Regex local (demora menos de 1 milissegundo)
                clean_text = self.cleaner.clean_diary(item.get("texto", ""))
                diarios_pre_limpos.append({
                    "titulo": item.get("titulo"),
                    "texto": clean_text
                })
            
            # Chama as Threads que criaste no teu extraction.py
            return self.extractor.extract_diaries_parallel(diarios_pre_limpos)
        except Exception as e:
            print(f"[ExtractionPipeline] Erro na execução paralela: {e}")
            return []