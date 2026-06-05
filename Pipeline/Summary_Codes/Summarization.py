import json
from pathlib import Path
from typing import Dict, Any

from Pipeline.llm import chat, get_client
from Pipeline.Prompts.Summary_Prompt import SUMMARY_TEXT_PROMPT
from Pipeline.Summary_Codes.json_to_text import change_data_format

class Summarizer:
    def __init__(self, system_prompt_path: Path):
        """Inicializa o cliente e carrega o System Prompt do ficheiro."""
        self.client = get_client()
        
        try:
            with open(system_prompt_path, 'r', encoding='utf-8') as f:
                
                self.system_prompt = f.read().strip()
        
        except Exception as e:

            self.system_prompt = "És um médico sénior. Resume o histórico clínico com precisão."
            
            print(f"Aviso: Não foi possível ler o System Prompt em {system_prompt_path}: {e}")

    def generate_summary(self, all_extractions: Dict[str, Any]) -> str:
        """Gera o sumário a partir dos dados estruturados da BD."""
        
        if not all_extractions:
            return "Nenhum dado disponível para sumarização."

        data_str = json.dumps(all_extractions, indent=2, ensure_ascii=False)
        
        data_format_text = change_data_format(data_str)
                
        user_prompt = SUMMARY_TEXT_PROMPT.format(extracted_data=data_format_text)
        
        summary, tempo_llm, houve_retry = chat(self.client, user_prompt, self.system_prompt)

        print(f"DEBUG LLM RESPONSE: '{summary}'")
        
        return summary.strip(), tempo_llm, houve_retry

