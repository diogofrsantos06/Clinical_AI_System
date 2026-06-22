import sys, time

from pathlib import Path
from typing import Dict, Any

from Pipeline.Extraction_Codes.extraction import DiaryExtractor
from Pipeline.Extraction_Codes.diary_cleaner import DiaryCleaner

BASE_DIR = Path(__file__).resolve().parent.parent 
sys.path.append(str(BASE_DIR))

class ExtractionPipeline:
    def __init__(self):
        self.extraction_prompt = BASE_DIR / "Pipeline" / "System_Prompts" / "Extraction.txt"
        self.cleaner = DiaryCleaner()
        self.extractor = DiaryExtractor(self.extraction_prompt)

    def run(self, raw_diary_text: str) -> Dict[str, Any]:
        try:
            clean_text = self.cleaner.clean_diary(raw_diary_text) #ELIMINAR A PARTE DO CLEAN_DIARY; IMPLICA MUDAR OU A BD OU METER O RAW TEXT PARA A BD
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
        
    def process_batch(self, list_of_diaries: list) -> list:
        """
        Processa um lote de diários de forma estritamente sequencial.
        Reutiliza o método 'run' para garantir a mesma limpeza e extração.
        """
        if not list_of_diaries:
            return []

        print(f"\n[PIPELINE] Iniciando processamento sequencial de {len(list_of_diaries)} diários...", flush=True)
        resultados_finais = []

        for i, item in enumerate(list_of_diaries):
            titulo = item.get("titulo", f"Diário_{i}")
            texto_bruto = item.get("texto", "")

            if not texto_bruto.strip():
                resultados_finais.append({"titulo": titulo, "status": "error", "message": "Texto vazio", "texto_original": texto_bruto})
                continue

            print(f"[{i+1}/{len(list_of_diaries)}] A extrair: '{titulo}'", flush=True)
            
            resultado = self.run(texto_bruto)
            
            resultado["titulo"] = titulo
            resultado["texto_original"] = texto_bruto
            resultados_finais.append(resultado)
            
        print("[PIPELINE] Processamento do lote concluído!\n", flush=True)
        return resultados_finais