import json, re, time
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

    def process_llm_section(self, user_prompt: str, section_name: str, schema: dict, fallbacks: dict) -> tuple:
        """
        Gere as 3 tentativas, valida o JSON contra o schema esperado e, em caso de falha total,
        tenta resgatar partes da resposta que estejam corretas (Resgate Parcial).
        """
        max_tentativas = 3
        
        for tentativa in range(1, max_tentativas + 1):
            try:
                resposta_raw, tempo, retry_llm = chat(self.client, user_prompt, self.system_prompt)
                resposta = resposta_raw[0] if isinstance(resposta_raw, (tuple, list)) else str(resposta_raw)
                
                if "504 Server Error" in resposta or "Gateway Timeout" in resposta:
                    raise ValueError("Timeout 504 detetado.")
                    
                match = re.search(r'\{.*\}', resposta, re.DOTALL)
                if not match:
                    raise ValueError("Nenhum bloco JSON válido encontrado na resposta.")
                    
                dados = json.loads(match.group(0))
                
                # VALIDAÇÃO DE SCHEMA ESTRUTURAL
                if not isinstance(dados, dict):
                    raise ValueError("O JSON retornado não é um Dicionário de base.")
                    
                for key, expected_type in schema.items():
                    if key not in dados:
                        raise ValueError(f"Chave obrigatória '{key}' está em falta.")
                    if not isinstance(dados[key], expected_type):
                        raise ValueError(f"A chave '{key}' tem o tipo errado. Esperado: {expected_type.__name__}.")
                
                # SUCESSO ABSOLUTO
                return dados, tempo, (retry_llm or tentativa > 1)

            except Exception as e:
                print(f"[{section_name}] Falha na tentativa {tentativa}/{max_tentativas}: {e}", flush=True)
                
                if tentativa < max_tentativas:
                    print(f"[{section_name}] A aguardar 5 segundos para recuperar...", flush=True)
                    time.sleep(5)
                else:
                    print(f"[{section_name}] Limite atingido! A aplicar resgate de dados parciais...", flush=True)
                    salvaged_data = {}
                    dados_parciais = {}
                    
                    # Tenta ler o que a LLM cuspiu na última tentativa, mesmo com erros
                    if 'resposta' in locals():
                        match_salvage = re.search(r'\{.*\}', resposta, re.DOTALL)
                        if match_salvage:
                            try:
                                dados_parciais = json.loads(match_salvage.group(0))
                            except:
                                pass # JSON totalmente ilegível, dados_parciais fica vazio
                    
                    for key, expected_type in schema.items():
                        if isinstance(dados_parciais, dict) and key in dados_parciais and isinstance(dados_parciais[key], expected_type):
                            salvaged_data[key] = dados_parciais[key]
                            print(f"[{section_name}] -> Chave '{key}' estava correta e foi resgatada!")
                        else:
                            salvaged_data[key] = fallbacks[key]
                            print(f"[{section_name}] -> Chave '{key}' corrompida. Substituída por mensagem segura de erro.")
                            
                    return salvaged_data, 0.0, True


    def generate_summary(self, all_extractions: Dict[str, Any]) -> tuple:
        if not all_extractions:
            return "Nenhum dado disponível para sumarização.", 0.0, False

        print("\n" + "-"*30 + " INÍCIO DA SUMARIZAÇÃO COM SCHEMA " + "-"*30)
        sumario_consolidado_dict = {}
        total_tempo_llm = 0.0
        algum_retry = False
        start_global = time.perf_counter()

        text_ant = change_data_format(all_extractions, seccao_alvo="diagnosticos")
        if text_ant:
            print(f"[ANTECEDENTES] Iniciado. Input: {len(text_ant)} chars.", flush=True)
            user_prompt = PROMPT_ANTECEDENTES.format(extracted_data=text_ant)
            
            schema = {"antecedentes": list}
            fallback = {"antecedentes": [{"diagnostico": "Erro: Não foi possível gerar o sumário de antecedentes.", "tipo": "N/A", "temporalidade": "N/A", "desde": "N/A"}]}
            
            dados, tempo, retry = self.process_llm_section(user_prompt, "ANTECEDENTES", schema, fallback)
            sumario_consolidado_dict.update(dados)
            total_tempo_llm += tempo
            if retry: algum_retry = True
        else:
            print("[ANTECEDENTES] Ignorado: Sem dados.", flush=True)

        text_med = change_data_format(all_extractions, seccao_alvo="medicacao")
        text_alergias = change_data_format(all_extractions, seccao_alvo="alergias")
        text_med_alergias = f"{text_med}\n\n{text_alergias}".strip()

        if text_med_alergias:
            print(f"[MEDICAÇÃO/ALERGIAS] Iniciado. Input: {len(text_med_alergias)} chars.", flush=True)
            user_prompt = PROMPT_MEDICACAO.format(extracted_data=text_med_alergias)
            
            schema = {"medicacao": list, "alergias": list}
            fallback = {
                "medicacao": [{"farmaco": "Erro: Não foi possível gerar o sumário de medicação.", "dosagem": "N/A", "posologia": "N/A", "indicacao": "N/A", "observacoes": "N/A"}],
                "alergias": ["Erro: Não foi possível gerar o sumário de alergias."]
            }
            
            dados, tempo, retry = self.process_llm_section(user_prompt, "MEDICAÇÃO/ALERGIAS", schema, fallback)
            sumario_consolidado_dict.update(dados)
            total_tempo_llm += tempo
            if retry: algum_retry = True
        else:
            print("[MEDICAÇÃO/ALERGIAS] Ignorado: Sem dados.", flush=True)

        text_ex = change_data_format(all_extractions, seccao_alvo="exames")
        if text_ex:
            print(f"[EXAMES] Iniciado. Input: {len(text_ex)} chars.", flush=True)
            user_prompt = PROMPT_EXAMES.format(extracted_data=text_ex)
            
            schema = {"exames": list}
            fallback = {"exames": [{"nome": "Erro de Processamento", "data": "N/A", "tipo_exame": "N/A", "resultado": "Erro: Não foi possível gerar o sumário de exames."}]}
            
            dados, tempo, retry = self.process_llm_section(user_prompt, "EXAMES", schema, fallback)
            sumario_consolidado_dict.update(dados)
            total_tempo_llm += tempo
            if retry: algum_retry = True
        else:
            print("[EXAMES] Ignorado: Sem dados.", flush=True)

        ultimo_titulo = list(all_extractions.keys())[-1]
        payload_recente = {ultimo_titulo: all_extractions[ultimo_titulo]}
        text_pl = change_data_format(payload_recente, seccao_alvo="plano")
        
        if text_pl:
            print(f"[PLANO] Iniciado. Focado em: '{ultimo_titulo}'.", flush=True)
            user_prompt = PROMPT_PLANO.format(extracted_data=text_pl)
            
            schema = {"plano": str} # Nota: O plano é a única string solta
            fallback = {"plano": "Erro: Não foi possível gerar o sumário para o plano terapêutico."}
            
            dados, tempo, retry = self.process_llm_section(user_prompt, "PLANO", schema, fallback)
            sumario_consolidado_dict.update(dados)
            total_tempo_llm += tempo
            if retry: algum_retry = True
        else:
            print("[PLANO] Ignorado: Sem dados.", flush=True)

        summary_final_limpo = json.dumps(sumario_consolidado_dict, ensure_ascii=False)
        
        print(f"\n[DEBUG METRICA] Tempo REAL global de sumarização: {time.perf_counter() - start_global:.2f}s")
        print(f"[DEBUG METRICA] Tempo LLM somado: {total_tempo_llm:.2f}s")
        print("-" * 30 + "\n")

        return summary_final_limpo.strip(), total_tempo_llm, algum_retry