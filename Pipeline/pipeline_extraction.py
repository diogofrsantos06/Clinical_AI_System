import sys
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent 
sys.path.append(str(BASE_DIR))

from Pipeline.Extraction_Codes.section_parser import LLMSectionParser
from Pipeline.Extraction_Codes.extraction import DiaryExtractor
from Pipeline.Extraction_Codes.diary_cleaner import DiaryCleaner

class ExtractionPipeline:
    def __init__(self):

        self.section_prompt = BASE_DIR / "Pipeline" / "System_Prompts" / "Section_Parser.txt"
        self.extraction_prompt = BASE_DIR / "Pipeline" / "System_Prompts" / "Extraction.txt"
        
        self.cleaner = DiaryCleaner()
        self.parser = LLMSectionParser(self.section_prompt)
        self.extractor = DiaryExtractor(self.extraction_prompt)

    def run(self, raw_diary_text: str) -> Dict[str, Any]:
        """
        Executa o fluxo automático: Texto Bruto -> Secções -> JSON Estruturado.
        """
        try:
            clean_text = self.cleaner.clean_diary(raw_diary_text)

            sections_obj = self.parser.parse(clean_text)
            sections_dict = sections_obj.to_dict()

            extracted_data = self.extractor.extract_full_diary(sections_dict)

            return {
                "status": "success",
                "cleaned_text": clean_text,
                "sections_text": sections_dict,    
                "extracted_json": extracted_data  
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro no processamento do pipeline: {str(e)}"
            }