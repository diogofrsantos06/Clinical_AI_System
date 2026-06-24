import json, re, time

from typing import Dict, Any

from Pipeline.llm import chat, get_client
from Pipeline.Prompts.Extraction_Prompt import get_prompt_for_diary_extraction

class DiaryExtractor:
    def __init__(self, system_prompt_path):
        """Inicializa o cliente e carrega as instruções do System Prompt"""
        
        self.client = get_client()

        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read().strip()
    
    def clean_json_response(self, response: str) -> str:
    
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

            try:
                return json.dumps(json.loads(candidate))
            except:
                pass

        print("RAW RESPONSE:")
        print(response)

        raise ValueError("JSON inválido")
    

    def extract_full_diary(self, diary_text: str) -> Dict[str, Any]:
        """
        Extrai um único diário num formato JSON estruturado.
        Inclui mecanismo de Retry (3 tentativas) para tolerância a falhas (ex: 504 Timeout).
        """
        
        user_prompt = get_prompt_for_diary_extraction(diary_text)
        max_tentativas = 3

        for tentativa in range(1, max_tentativas + 1):
            try:
                response, tempo_llm, houve_retry = chat(self.client, user_prompt, self.system_prompt)
                
                json_str = self.clean_json_response(response)
                dados = json.loads(json_str)

                if not isinstance(dados, dict):
                    raise ValueError("A resposta da LLM não é um objeto JSON válido.")
                
                chaves_lista = ["diagnosticos", "medicacao", "alergias", "exames", "sintomas", "plano"]
                for chave in chaves_lista:
                    if chave in dados and not isinstance(dados[chave], list):
                        raise ValueError(f"Formato quebrado: A secção '{chave}' devia ser uma lista, mas a LLM devolveu {type(dados[chave]).__name__}.")

                return {
                    "dados": dados,
                    "tempo_llm": tempo_llm,
                    "houve_retry": houve_retry or (tentativa > 1),
                    "status": "success"
                }

            except Exception as e:
                print(f"[EXTRAÇÃO] Falha na tentativa {tentativa}/{max_tentativas}: {str(e)}", flush=True)
                
                if tentativa < max_tentativas:
                    print("[EXTRAÇÃO] A aguardar 5 segundos para arrefecer o servidor antes de tentar novamente...", flush=True)
                    time.sleep(5)  
                else:
                    print("[EXTRAÇÃO] Limite de tentativas atingido! A criar registo vazio para não bloquear o pipeline.", flush=True)
                    
                    return {
                        "dados": {}, 
                        "tempo_llm": 0.0,
                        "houve_retry": True,
                        "status": "success" 
                    }
        
    