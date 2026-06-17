import json, re
from pathlib import Path
from typing import Dict, Any

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
        """Gera o sumário dividindo a análise em 4 chamadas focadas e sequenciais."""        
        
        if not all_extractions:
            return "Nenhum dado disponível para sumarização.", 0.0, False
        
        total_tempo_llm = 0.0
        algum_retry_aconteceu = False
        sumario_consolidado_dict = {}

        # FASE 1: ANTECEDENTES E DIAGNÓSTICOS
        text_antecedentes = change_data_format(all_extractions, seccao_alvo="diagnosticos")
        if text_antecedentes:
            user_prompt = PROMPT_ANTECEDENTES.format(extracted_data=text_antecedentes)
            summary, tempo, retry = chat(self.client, user_prompt, self.system_prompt)
            total_tempo_llm += tempo
            if retry: algum_retry_aconteceu = True
            
            match = re.search(r'\{.*\}', summary, re.DOTALL)
            if match:
                try:
                    sumario_consolidado_dict.update(json.loads(match.group(0)))
                except Exception as e:
                    print(f"[Summarizer] Erro ao fundir Antecedentes: {e}")

        # FASE 2: MEDICAÇÃO E ALERGIAS
        text_med = change_data_format(all_extractions, seccao_alvo="medicacao")
        text_alergias = change_data_format(all_extractions, seccao_alvo="alergias")
        text_med_alergias = f"{text_med}\n\n{text_alergias}".strip()

        if text_med_alergias:
            user_prompt = PROMPT_MEDICACAO.format(extracted_data=text_med_alergias)
            summary, tempo, retry = chat(self.client, user_prompt, self.system_prompt)
            total_tempo_llm += tempo
            if retry: algum_retry_aconteceu = True
            
            match = re.search(r'\{.*\}', summary, re.DOTALL)
            if match:
                try:
                    sumario_consolidado_dict.update(json.loads(match.group(0)))
                except Exception as e:
                    print(f"[Summarizer] Erro ao fundir Medicação/Alergias: {e}")

        # FASE 3: EXAMES E RESULTADOS
        text_exames = change_data_format(all_extractions, seccao_alvo="exames")
        if text_exames:
            user_prompt = PROMPT_EXAMES.format(extracted_data=text_exames)
            summary, tempo, retry = chat(self.client, user_prompt, self.system_prompt)
            total_tempo_llm += tempo
            if retry: algum_retry_aconteceu = True
            
            match = re.search(r'\{.*\}', summary, re.DOTALL)
            if match:
                try:
                    sumario_consolidado_dict.update(json.loads(match.group(0)))
                except Exception as e:
                    print(f"[Summarizer] Erro ao fundir Exames: {e}")

        # FASE 4: PLANO TERAPÊUTICO 
        if all_extractions:
            # Como os diários entram ordenados cronologicamente, pegamos no último elemento
            ultimo_titulo = list(all_extractions.keys())[-1]
            ultimo_conteudo = all_extractions[ultimo_titulo]
            payload_recente = {ultimo_titulo: ultimo_conteudo}
            
            text_plano = change_data_format(payload_recente, seccao_alvo="plano")
            if text_plano:
                user_prompt = PROMPT_PLANO.format(extracted_data=text_plano)
                summary, tempo, retry = chat(self.client, user_prompt, self.system_prompt)
                total_tempo_llm += tempo
                if retry: algum_retry_aconteceu = True
                
                match = re.search(r'\{.*\}', summary, re.DOTALL)
                if match:
                    try:
                        sumario_consolidado_dict.update(json.loads(match.group(0)))
                    except Exception as e:
                        print(f"[Summarizer] Erro ao fundir Plano: {e}")

        # Serializa o dicionário consolidado final de volta para String JSON
        summary_final_limpo = json.dumps(sumario_consolidado_dict, ensure_ascii=False)
        
        return summary_final_limpo.strip(), total_tempo_llm, algum_retry_aconteceu

