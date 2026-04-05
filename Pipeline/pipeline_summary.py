import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
SUMMARY_SYSTEM_PROMPT_PATH = BASE_DIR / "Pipeline" / "System_Prompts" / "Summary.txt"

from Summary_Codes.Summarization import Summarizer

class SummaryPipeline:
    def __init__(self):
        self.summarizer = Summarizer(system_prompt_path=SUMMARY_SYSTEM_PROMPT_PATH)

    def run_summary(self, list_of_extractions: list) -> str:
        """
        Entrada: Lista de DIÁRIOS EXTRAÍDOS (JSON) vindos da BD.
        Saída: Texto do sumário final.
        """
        # Organizamos as extrações num dicionário para a IA saber qual é qual
        structured_payload = {}
        for idx, extraction in enumerate(list_of_extractions):
            diary_label = f"Diário_{idx + 1}"
            structured_payload[diary_label] = extraction

        return self.summarizer.generate_summary(structured_payload)


#Teste 
'''
if __name__ == "__main__":
    print("Iniciando Teste da Pipeline de Sumarização...")

    PATIENT_ID = "Patient_test2"
    EXTRACTIONS_DIR = BASE_DIR / "Pipeline" / "Patients" / PATIENT_ID / "sections"
    
    extraction_files = sorted(EXTRACTIONS_DIR.glob("extraction_output_*.json"))

    if not extraction_files:
        print(f"Erve: Não foram encontrados ficheiros JSON em {EXTRACTIONS_DIR}")
    else:
        # 3. Carregar os dados estruturados para uma lista
        list_of_data = []
        for f_path in extraction_files:
            with open(f_path, 'r', encoding='utf-8') as f:
                list_of_data.append(json.load(f))
        
        print(f"✅ Carregados {len(list_of_data)} diários extraídos.")

        # 4. Executar a Pipeline
        pipeline = SummaryPipeline()
        print("⏳ A comunicar com a LLM para gerar o sumário consolidado...")
        
        try:
            resumo_final = pipeline.run_summary(list_of_data)
            
            print("\n" + "="*60)
            print("SUMÁRIO GERADO:")
            print("="*60)
            print(resumo_final)
            print("="*60)
            
            # 5. Opcional: Guardar o resultado do teste num ficheiro de texto
            output_path = EXTRACTIONS_DIR / "debug_summary_result.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(resumo_final)
            print(f"\n💾 Sumário guardado para revisão em: {output_path.name}")

        except Exception as e:
            print(f"❌ Erro durante a execução: {e}")
            '''