import json
import sys
import time
import re
from typing import Dict, Any, List
from urllib import response
from concurrent.futures import ThreadPoolExecutor

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

        print("RAW RESPONSE:")
        print(response)

        raise ValueError("JSON inválido")
    

    def extract_full_diary(self, diary_text: str) -> Dict[str, Any]:
        """
        Extrai todo o diário num único JSON estruturado.
        """
        user_prompt = get_prompt_for_diary_extraction(diary_text)

        try:
            response, tempo_llm, houve_retry = chat(self.client, user_prompt, self.system_prompt)

            json_str = self._clean_json_response(response)
            dados = json.loads(json_str)

            return {
                "dados": dados,
                "tempo_llm": tempo_llm,
                "houve_retry": houve_retry,
                "status": "success"
            }

        except Exception as e:
            print(f"Erro na extração do diário: {e}")
            return {"status": "error", "message": str(e)}
        
    def extract_diaries_parallel(self, list_of_diaries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Recebe uma lista de dicionários contendo o título e o texto bruto do diário.
        Exemplo: [{"titulo": "Consulta A", "texto": "..."}, {"titulo": "Consulta B", "texto": "..."}]
        Dispara as extrações estruturadas todas ao mesmo tempo.
        """
        if not list_of_diaries:
            return []

        print(f"\n[EXTRAÇÃO ESTRUTURADA] Disparando {len(list_of_diaries)} diários em paralelo para a LLM...", flush=True)
        start_global = time.perf_counter()

        def worker(diary_item):
            titulo = diary_item.get("titulo", "Diário Desconhecido")
            texto_bruto = diary_item.get("texto", "")
            
            if not texto_bruto.strip():
                return {"titulo": titulo, "status": "error", "message": "Texto vazio"}

            print(f"[THREAD-EXTRAÇÃO] Iniciando estruturação de dados: '{titulo}'", flush=True)
            start_thread = time.perf_counter()
            
            resultado = self.extract_full_diary(texto_bruto)
            
            tempo_decorrido = time.perf_counter() - start_thread
            print(f"[THREAD-EXTRAÇÃO] Terminou: '{titulo}' em {tempo_decorrido:.2f}s", flush=True)
            
            return {
                "titulo": titulo,
                "dados": resultado.get("dados"),
                "tempo_llm": resultado.get("tempo_llm", 0.0),
                "houve_retry": resultado.get("houve_retry", False),
                "status": resultado.get("status")
            }

        with ThreadPoolExecutor(max_workers=len(list_of_diaries)) as executor:
            resultados_finais = list(executor.map(worker, list_of_diaries))

        tempo_global_real = time.perf_counter() - start_global
        print(f"[DEBUG EXTRAÇÃO] Todas as estruturações terminaram em paralelo! Tempo REAL total: {tempo_global_real:.2f}s\n")
        
        return resultados_finais
    

        