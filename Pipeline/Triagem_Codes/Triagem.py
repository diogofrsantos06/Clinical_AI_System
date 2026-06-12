import json
import re
from Pipeline.llm import chat, get_client
from Pipeline.Prompts.Triagem_Prompt import TRIAGEM_PROMPT

class TriageAnalyzer:

    def __init__(self, system_prompt_path):
        self.client = get_client()
        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read().strip()

    def analyze(self, triage_text: str, patient_history: dict):
        # DEBUG: Confirmar o que estamos a enviar
        print(f"DEBUG ANALYZER: Tipo de patient_history: {type(patient_history)}")
        
        # Se for string, tentamos converter para dict antes do dumps
        if isinstance(patient_history, str):
            try:
                patient_history = json.loads(patient_history)
            except:
                pass 

        history_str = json.dumps(patient_history, indent=2, ensure_ascii=False)
        user_prompt = TRIAGEM_PROMPT.format(triagem=triage_text, data=history_str)
        
        response, tempo_llm, houve_retry = chat(self.client, user_prompt, self.system_prompt)
        
        # DEBUG: Ver o que a IA respondeu antes de processar
        print(f"DEBUG ANALYZER: Resposta bruta da IA: {response[:200]}...")
        
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        
        json_data = {}
        texto_clinico = response
        
        if "[JSON_START]" in response:
            # Divide a resposta em duas partes usando a tag
            partes = response.split("[JSON_START]")
            texto_clinico = partes[0].strip()
            json_str = partes[1].strip()
            
            texto_clinico = re.sub(r'(:|são:)\s*$', '.', texto_clinico).strip()
            
            json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group())
                    print(f"DEBUG ANALYZER: JSON extraído com sucesso. Chaves: {list(json_data.keys())}")
                except Exception as e:
                    print(f"DEBUG ANALYZER: Falha no JSON load após split: {e}")
        else:
            print("DEBUG ANALYZER: Tag [JSON_START] não encontrada! A tentar fallback...")
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group())
                    texto_clinico = response.replace(json_match.group(), "").strip()
                except Exception as e:
                    pass

        return texto_clinico, json_data, tempo_llm, houve_retry