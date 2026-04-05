import sys
import json
from pathlib import Path
from typing import Dict, Any

# Setup de caminhos para encontrar o groq_client e os prompts
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from groq_client import chat, get_client
from Prompts.Summary_Prompt import SUMMARY_TEXT_PROMPT

class Summarizer:
    def __init__(self, system_prompt_path: Path):
        """Inicializa o cliente e carrega o System Prompt do ficheiro."""
        self.client = get_client()
        
        # Carregamento dinâmico do System Prompt
        try:
            with open(system_prompt_path, 'r', encoding='utf-8') as f:
                self.system_prompt = f.read().strip()
        except Exception as e:
            # Fallback caso o ficheiro falhe
            self.system_prompt = "És um médico sénior. Resume o histórico clínico com precisão."
            print(f"Aviso: Não foi possível ler o System Prompt em {system_prompt_path}: {e}")

    def generate_summary(self, all_extractions: Dict[str, Any]) -> str:
        """Gera o sumário a partir dos dados estruturados da BD."""
        if not all_extractions:
            return "Nenhum dado disponível para sumarização."

        # Prepara a string JSON com todos os diários para a LLM
        data_str = json.dumps(all_extractions, indent=2, ensure_ascii=False)
        
        # Injeta os dados no molde (User Prompt)
        user_prompt = SUMMARY_TEXT_PROMPT.format(extracted_data=data_str)
        
        # Usa a função chat do teu groq_client.py
        summary = chat(self.client, user_prompt, self.system_prompt)
        
        return summary.strip()

