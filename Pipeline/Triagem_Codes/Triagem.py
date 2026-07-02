import json, re, time
from Pipeline.llm import chat, get_client
from Pipeline.Prompts.Triagem_Prompt import TRIAGEM_PROMPT

class TriageAnalyzer:

    def __init__(self, system_prompt_path):
        self.client = get_client()
        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read().strip()

    def analyze(self, triage_text: str, patient_history: dict):

        if isinstance(patient_history, str):
            try:
                patient_history = json.loads(patient_history)
            except:
                pass 

        history_str = json.dumps(patient_history, indent=2, ensure_ascii=False)
        user_prompt = TRIAGEM_PROMPT.format(triagem=triage_text, data=history_str)
        
        max_tentativas = 3
        
        for tentativa in range(1, max_tentativas + 1):
            try:
                response_raw, tempo_llm, retry_llm = chat(self.client, user_prompt, self.system_prompt)
                response = response_raw[0] if isinstance(response_raw, (tuple, list)) else str(response_raw)
                
                if "504 Server Error" in response or "Gateway Timeout" in response:
                    raise ValueError("Timeout 504 detetado.")
                
                json_data = {}
                texto_clinico = response
                
                if "[JSON_START]" in response:
                    partes = response.split("[JSON_START]")
                    texto_clinico = re.sub(r'(:|são:)\s*$', '.', partes[0].strip()).strip()
                    json_str = partes[1].strip()
                    
                    json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
                    if not json_match: raise ValueError("Nenhum JSON válido após a tag.")
                    json_data = json.loads(json_match.group())
                else:
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if not json_match: raise ValueError("Tag e JSON ausentes.")
                    json_data = json.loads(json_match.group())
                    texto_clinico = response.replace(json_match.group(), "").strip()

                if "triagem" not in json_data: 
                    raise ValueError("O JSON não contém a chave obrigatória 'triagem'.")
                if "exames" not in json_data:
                    raise ValueError("O JSON não contém a chave obrigatória 'exames'.")

                return texto_clinico, json_data, tempo_llm, (retry_llm or tentativa > 1)

            except Exception as e:
                print(f"[TRIAGEM] Falha na tentativa {tentativa}/{max_tentativas}: {e}", flush=True)
                if tentativa < max_tentativas:
                    time.sleep(5)
                else:
                    print("[TRIAGEM] Limite atingido! A devolver fallback de segurança.", flush=True)
                    return "Não foi possível realizar a análise clínica.", {"triagem": "Erro de sistema na inferência."}, 0.0, True