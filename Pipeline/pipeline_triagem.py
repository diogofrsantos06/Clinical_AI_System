from pathlib import Path
from Pipeline.Triagem_Codes.Triagem import TriageAnalyzer

BASE_DIR = Path(__file__).resolve().parent.parent
TRIAGE_SYSTEM_PROMPT_PATH = BASE_DIR / "Pipeline" / "System_Prompts" / "Triagem.txt"

class TriagePipeline:
    def __init__(self):
        self.analyzer = TriageAnalyzer(system_prompt_path=TRIAGE_SYSTEM_PROMPT_PATH)

    def run(self, triage_text: str, patient_history: dict):
        try:
            print("DEBUG PIPELINE: A chamar self.analyzer.analyze...")
            result = self.analyzer.analyze(triage_text, patient_history)
            
            # Verificamos se o resultado é o que esperamos
            if not isinstance(result, tuple) or len(result) < 4:
                print(f"DEBUG PIPELINE: O analyzer retornou algo inesperado: {result}")
                return {"error": "Formato de retorno inválido do analyzer"}

            texto, dados_json, tempo, retry = result
            
            # Verifica se 'triagem' existe nos dados ANTES de retornar
            if 'triagem' not in dados_json:
                 print(f"DEBUG PIPELINE: ALERTA - Chave 'triagem' não encontrada em: {dados_json}")

            return {
                "analise_texto": texto,
                "dados_estruturados": dados_json,
                #"tempo_llm": tempo,
                #"houve_retry": retry
            }
        
        except Exception as e:
            # Captura o erro exato e a linha onde ocorre
            import traceback
            print(f"DEBUG PIPELINE: ERRO CRÍTICO -> {str(e)}")
            traceback.print_exc() # Isto vai mostrar a linha exata do erro
            return {"error": str(e), "analise_texto": "", "dados_estruturados": {}}