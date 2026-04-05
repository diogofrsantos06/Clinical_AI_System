import json
import sys
import time
import re
from pathlib import Path
from typing import Dict, Any, List
from urllib import response

sys.path.append(str(Path(__file__).resolve().parent.parent))
from groq_client import chat, get_client

sys.path.append(str(Path(__file__).resolve().parent.parent / "Prompts"))
from Extraction_Prompt import get_prompt_for_section

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
        match = re.search(r'\{.*?\}|\[.*?\]', text, re.DOTALL)
        if match:
            candidate = match.group(0)

            # 4. Tentar corrigir aspas simples → duplas (fallback)
            try:
                return json.dumps(json.loads(candidate))
            except:
                try:
                    fixed = candidate.replace("'", '"')
                    return json.dumps(json.loads(fixed))
                except:
                    pass

        # 5. Último recurso: tentar encontrar JSON maior possível (greedy)
        match = re.search(r'\{.*\}|\[.*\]', text, re.DOTALL)
        if match:
            candidate = match.group(0)
            try:
                return json.dumps(json.loads(candidate))
            except:
                pass

        # DEBUG útil
        print("⚠️ RESPOSTA ORIGINAL DA LLM:")
        print(response)

        raise ValueError("Não foi possível extrair JSON válido da resposta")
    
    def extract_section_content(self, section_name: str, section_text: str) -> Any:
        """
        Gera a extração para uma única gaveta (secção) usando o molde específico.
        """
        if not section_text or len(section_text.strip()) < 5:
            return [] 

        user_prompt = get_prompt_for_section(section_name, section_text)
        
        try:
            response = chat(self.client, user_prompt, self.system_prompt)
            
            json_str = self._clean_json_response(response)
            data = json.loads(json_str)
            
            # Garante que o resultado é a parte que nos interessa
            # Se a IA devolver {"terapeutica": [...]}, extraímos apenas a lista
            if isinstance(data, dict) and section_name in data:
                return data[section_name]
            return data

        except Exception as e:
            print(f"Erro na extração da secção [{section_name}]: {e}")
            return {"erro": "Falha no parse", "conteudo_original": section_text}

    def extract_full_diary(self, sections_dict: Dict[str, str]) -> Dict[str, Any]:
        """
        Percorre todas as secções de um diário e monta o JSON final estruturado.
        """
        final_extraction = {}
        
        for name, text in sections_dict.items():
            if name == "data":
                final_extraction["data"] = text
                continue

            print(f"   Extraindo: {name}...")
            time.sleep(1.2) 
            
            final_extraction[name] = self.extract_section_content(name, text)
            
        return final_extraction
    

# Teste 
'''
if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    SYSTEM_PROMPT_PATH = BASE_DIR / "System_Prompts" / "Extraction.txt"
    
    PATIENT_ID = "Patient_test2"
    SECTIONS_DIR = BASE_DIR / "Patients" / PATIENT_ID / "sections"
    
    extractor = DiaryExtractor(SYSTEM_PROMPT_PATH)

    # Opção A: Testar apenas um diário específico
    test_file = SECTIONS_DIR / "cleaned_diary_02_sections.json" 
    
    # Opção B (Comentada): Testar todos os ficheiros da pasta
    #diary_files = sorted(SECTIONS_DIR.glob("diary_*_sections.json"))

    if test_file.exists():
        print(f"A ler secções de: {test_file.name}")
        
        with open(test_file, 'r', encoding='utf-8') as f:
            mock_sections = json.load(f)

        print(f"A iniciar extração estruturada para {test_file.name}...")
        
        try:
            start_time = time.time()
            resultado_final = extractor.extract_full_diary(mock_sections)
            end_time = time.time()

            print(f"RESULTADO FINAL ({test_file.stem}):")
            print(json.dumps(resultado_final, indent=2, ensure_ascii=False))
            
            # Opcional: Guardar o teste numa pasta 'debug' para analisares no VS Code
            debug_path = SECTIONS_DIR / "extraction_output_2.json"
            with open(debug_path, 'w', encoding='utf-8') as f:
                json.dump(resultado_final, f, indent=2, ensure_ascii=False)
            print(f"\nResultado guardado para análise em: {debug_path}")

        except Exception as e:
            print(f"Erro na extração: {e}")
    else:
        print(f"Ficheiro não encontrado em: {test_file}")
        print(f"Verifica se correstes o section_parser.py primeiro.")
        '''