import json
import sys
import time
import re
from typing import Dict, Any, List
from urllib import response

from Pipeline.llm import chat, get_client
from Pipeline.Prompts.Extraction_Prompt import get_prompt_for_diary_extraction

class DiaryExtractor:
    def __init__(self, system_prompt_path):
        """Inicializa o cliente e carrega as instruções de mestre (System Prompt)"""
        
        self.client = get_client()

        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read().strip()
    
    def _clean_json_response(self, response: str) -> str:
    
        if not response:
            raise ValueError("Resposta vazia da LLM")

        text = response.strip()

        # 1. Remover blocos ```json ``` se existirem
        text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
        text = re.sub(r"```", "", text)

        # 2. Tentar parse direto primeiro (fast path)
        try:
            json.loads(text)
            return text
        except:
            pass

        # 3. Extrair o primeiro bloco JSON válido (não greedy)
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            candidate = match.group(0)

            # 4. Tentar corrigir aspas simples → duplas (fallback)
            try:
                return json.dumps(json.loads(candidate))
            except:
                pass

        print("⚠️ RAW RESPONSE:")
        print(response)

        raise ValueError("JSON inválido")
    

    def extract_full_diary(self, diary_text: str) -> Dict[str, Any]:
        """
        Extrai todo o diário num único JSON estruturado.
        """
        user_prompt = get_prompt_for_diary_extraction(diary_text)

        try:
            response = chat(self.client, user_prompt, self.system_prompt)

            json_str = self._clean_json_response(response)
            return json.loads(json_str)

        except Exception as e:
            print(f"Erro na extração do diário: {e}")
            return {
                "erro": "falha_extracao",
                "conteudo_original": diary_text
            }
    
