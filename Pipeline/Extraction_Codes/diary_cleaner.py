import re
import os
from pathlib import Path

class DiaryCleaner:
    def __init__(self):
        #RETIRAR DICIONARIO DÁ ERRO
        self.abbreviation_map = {
            r'\bid\b': 'uma vez por dia',
            r'\bbid\b': 'duas vezes por dia',
            r'\btid\b': 'três vezes por dia',
            r'\bqid\b': 'quatro vezes por dia',
            r'\bSOS\b': 'se necessário',
            r'\bprn\b': 'se necessário',
            r'\bEV\b': 'endovenoso',
            r'\bVO\b': 'via oral',
            r'\bDx\b': 'diagnóstico',
            r'\bTx\b': 'tratamento',
            r'\bHx\b': 'história',
            r'\bEx\b': 'exame',
        }
        
        self.unit_map = {
            r'(\d+)\s*mg\b': r'\1 miligramas',
            r'(\d+)\s*g\b(?!\w)': r'\1 gramas',
            r'(\d+)\s*ml\b': r'\1 mililitros',
            r'(\d+)\s*kg\b': r'\1 quilogramas',
        }

    def clean_diary(self, diary_text: str) -> str:

        if not diary_text:
            return ""
        
        # Elimina quebras de linha excessivas
        text = diary_text.replace('\\n', '\n')

        # Elimina o cabeçalho deixando a data
        header_pattern = r'^(\d{1,2}[-/][\w\d]{2,10}[-/]\d{2,4})[^\n]*(\n|$)'
        text = re.sub(header_pattern, r'\1\n\n', text, flags=re.MULTILINE)

        # Normalizar parágrafos
        lines = [line.strip() for line in text.split('\n')]
        
        # Mantém parágrafos mas remove o "lixo" de \n do texto
        processed_lines = []
        for line in lines:
            if line:
                processed_lines.append(line)
            elif processed_lines and processed_lines[-1] != "":
                processed_lines.append("")

        text = '\n'.join(processed_lines)

        # Aplica os dicionários 
        #text = self._normalize_abbreviations(text)
        #text = self._normalize_units(text)

        # Limpa espaços duplos
        text = re.sub(r' +', ' ', text)

        return text.strip()

    def _normalize_abbreviations(self, text: str) -> str:
        for pattern, replacement in self.abbreviation_map.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    def _normalize_units(self, text: str) -> str:
        for pattern, replacement in self.unit_map.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text


'''
if __name__ == "__main__":

    BASE_DIR = Path(__file__).resolve().parent.parent 
    INPUT_DIR = BASE_DIR / 'Patients' / 'Patient_test2' / 'diaries'
    OUTPUT_DIR = INPUT_DIR / 'cleaned'

    if not INPUT_DIR.exists():
        print(f"Erro: Pasta não encontrada em {INPUT_DIR.absolute()}")
    else:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cleaner = DiaryCleaner()
        
        files = list(INPUT_DIR.glob("*.txt"))
        print(f"Encontrados {len(files)} ficheiros.")

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                cleaned = cleaner.clean_diary(content)
                
                output_path = OUTPUT_DIR / f"cleaned_{file_path.name}"
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned)
                
            except Exception as e:
                print(f"Erro em {file_path.name}: {e}")

#Correr python diary_cleaner.py para testar, na diretoria Pipeline/Extraction_Codes
'''