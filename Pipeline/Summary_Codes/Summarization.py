import json, re
from pathlib import Path
from typing import Dict, Any

from concurrent.futures import ThreadPoolExecutor

from Pipeline.llm import chat, get_client
from Pipeline.Prompts.Summary_Prompt import PROMPT_ANTECEDENTES, PROMPT_MEDICACAO, PROMPT_EXAMES, PROMPT_PLANO
from Pipeline.Summary_Codes.json_to_text import change_data_format

class Summarizer:
    def __init__(self, system_prompt_path: Path):
        """Inicializa o cliente e carrega o System Prompt do ficheiro."""
        self.client = get_client()
        
        try:
            with open(system_prompt_path, 'r', encoding='utf-8') as f:
                
                self.system_prompt = f.read().strip()
        
        except Exception as e:

            self.system_prompt = "És um médico sénior. Resume o histórico clínico com precisão."
            
            print(f"Aviso: Não foi possível ler o System Prompt em {system_prompt_path}: {e}")

    def generate_summary(self, all_extractions: Dict[str, Any]) -> tuple:
        if not all_extractions:
            return "Nenhum dado disponível para sumarização.", 0.0, False

        sumario_consolidado_dict = {}
        
        # Funções auxiliares locais para podermos disparar em paralelo
        def executar_antecedentes():
            text = change_data_format(all_extractions, seccao_alvo="diagnosticos")
            if text:
                user_prompt = PROMPT_ANTECEDENTES.format(extracted_data=text)
                return chat(self.client, user_prompt, self.system_prompt)
            return None

        def executar_medicacao():
            text_med = change_data_format(all_extractions, seccao_alvo="medicacao")
            text_alergias = change_data_format(all_extractions, seccao_alvo="alergias")
            text_med_alergias = f"{text_med}\n\n{text_alergias}".strip()
            if text_med_alergias:
                user_prompt = PROMPT_MEDICACAO.format(extracted_data=text_med_alergias)
                return chat(self.client, user_prompt, self.system_prompt)
            return None

        def executar_exames():
            text = change_data_format(all_extractions, seccao_alvo="exames")
            if text:
                user_prompt = PROMPT_EXAMES.format(extracted_data=text)
                return chat(self.client, user_prompt, self.system_prompt)
            return None

        def executar_plano():
            ultimo_titulo = list(all_extractions.keys())[-1]
            ultimo_conteudo = all_extractions[ultimo_titulo]
            payload_recente = {ultimo_titulo: ultimo_conteudo}
            text = change_data_format(payload_recente, seccao_alvo="plano")
            if text:
                user_prompt = PROMPT_PLANO.format(extracted_data=text)
                return chat(self.client, user_prompt, self.system_prompt)
            return None

        # Disparar as 4 chamadas simultaneamente para a API/Ollama
        total_tempo_llm = 0.0
        algum_retry = False

        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submete as tarefas para correrem ao mesmo tempo
            futuro_ant = executor.submit(executar_antecedentes)
            futuro_med = executor.submit(executar_medicacao)
            futuro_ex = executor.submit(executar_exames)
            futuro_pl = executor.submit(executar_plano)

            # Recolhe os resultados à medida que vão terminando
            res_ant = futuro_ant.result()
            res_med = futuro_med.result()
            res_ex = futuro_ex.result()
            res_pl = futuro_pl.result()

        # Processar os resultados recolhidos
        mapeamento_resultados = [
            (res_ant, "Antecedentes"),
            (res_med, "Medicação"),
            (res_ex, "Exames"),
            (res_pl, "Plano")
        ]

        for res, nome_fase in mapeamento_resultados:
            if res:
                summary, tempo, retry = res
                total_tempo_llm += tempo  # Mantém a métrica de tempo acumulado correta
                if retry: algum_retry = True
                
                match = re.search(r'\{.*\}', summary, re.DOTALL)
                if match:
                    try:
                        sumario_consolidado_dict.update(json.loads(match.group(0)))
                    except Exception as e:
                        print(f"[Summarizer] Erro ao fundir {nome_fase}: {e}")

        summary_final_limpo = json.dumps(sumario_consolidado_dict, ensure_ascii=False)
        return summary_final_limpo.strip(), total_tempo_llm, algum_retry

