import json, re, time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timedelta

from Pipeline.llm import chat, get_client
from Pipeline.Prompts.Summary_Prompt import PROMPT_ANTECEDENTES, PROMPT_MEDICACAO, PROMPT_EXAMES, PROMPT_PLANO
from Pipeline.Summary_Codes.json_to_text import change_data_format

def extract_date_from_title(title: str) -> datetime:
    match = re.search(r'(\d{1,2})[-/]([a-zA-Z]{3}|\d{1,2})[-/](\d{2,4})', title)
    if not match: return datetime.min 
    dia, mes_str, ano_str = match.groups()
    ano = int(ano_str)
    if ano < 100: ano += 2000 
    dia = int(dia)
    meses = {'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6, 'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12}
    mes = meses.get(mes_str.lower(), 1)
    try: return datetime(ano, mes, dia)
    except ValueError: return datetime.min

class Summarizer:
    def __init__(self, system_prompt_path: Path,client=None):
        """Inicializa o cliente e carrega o System Prompt do ficheiro."""
        self.client = client if client else get_client()
        
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
                    raise ValueError(f"Formato JSON não encontrado. Resposta recebida: {resposta[:50]}...")
                
                json_str = match.group(0)
                dados = json.loads(json_str)
                
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
        tempos_seccoes = {}
        algum_retry = False
        start_global = time.perf_counter()

        # 1. ANTECEDENTES
        start_sec = time.perf_counter()
        text_ant = change_data_format(all_extractions, seccao_alvo="diagnosticos")
        if text_ant:
            print(f"[ANTECEDENTES] Iniciado. Input: {len(text_ant)} chars.", flush=True)
            user_prompt = PROMPT_ANTECEDENTES.format(extracted_data=text_ant)
            
            schema = {"antecedentes": list}
            fallback = {"antecedentes": [{"diagnostico": "Erro: Não foi possível gerar o sumário de antecedentes.", "tipo": "N/A", "temporalidade": "N/A", "desde": "N/A"}]}
            
            dados, tempo, retry = self.process_llm_section(user_prompt, "ANTECEDENTES", schema, fallback)
            sumario_consolidado_dict.update(dados)
            if retry: algum_retry = True
            tempos_seccoes["MEDICAÇÃO"] = {"duration": time.perf_counter() - start_sec, "inference": tempo}
        else:
            print("[ANTECEDENTES] Ignorado: Sem dados.", flush=True)

        # 2. MEDICAÇÃO E ALERGIAS
        start_sec = time.perf_counter()
        data_limite = datetime.now() - timedelta(days=547) # 1.5 anos
        
        temp_especialidades = {} 

        for titulo, conteudo in all_extractions.items():
            data_consulta = extract_date_from_title(titulo)
            if data_consulta < data_limite: continue
            
            meds = conteudo.get("medicacao", [])
            if not meds: continue 
                
            esp = titulo.split(" - ")[0].strip()
            if esp not in temp_especialidades: temp_especialidades[esp] = []
            temp_especialidades[esp].append({'data': data_consulta, 'titulo': titulo, 'meds': meds})

        medicacao_filtrada = {}
        for esp, lista_consultas in temp_especialidades.items():
            lista_consultas.sort(key=lambda x: x['data'], reverse=True)
            melhor_consulta = lista_consultas[0]
            medicacao_filtrada[esp] = {'titulo': melhor_consulta['titulo'], 'dados': melhor_consulta['meds']}

        dataset_med_filtrado = {info['titulo']: {"medicacao": info['dados']} for info in medicacao_filtrada.values()}
        
        text_med = change_data_format(dataset_med_filtrado, seccao_alvo="medicacao")
        text_alergias = change_data_format(all_extractions, seccao_alvo="alergias") # Alergias mantém-se completo
        text_med_alergias = f"{text_med}\n\n{text_alergias}".strip()

        if text_med_alergias:
            print(f"[MEDICAÇÃO/ALERGIAS] Iniciado. Input: {len(text_med_alergias)} chars.", flush=True)
            user_prompt = PROMPT_MEDICACAO.format(extracted_data=text_med_alergias)
            
            schema = {"medicacao": list, "alergias": list}
            fallback = {
                "medicacao": [{"farmaco": "N/A", "dosagem": "N/A", "posologia": "N/A", "indicacao": "N/A", "diario_origem": "N/A"}],
                "alergias": [{"substancia": "N/A", "reacao": "N/A", "registo_origem": "N/A"}]
            }
            
            dados, tempo, retry = self.process_llm_section(user_prompt, "MEDICAÇÃO/ALERGIAS", schema, fallback)
            sumario_consolidado_dict.update(dados)
            if retry: algum_retry = True
            tempos_seccoes["MEDICAÇÃO"] = {"duration": time.perf_counter() - start_sec, "inference": tempo}
        else:
            print("[MEDICAÇÃO/ALERGIAS] Ignorado: Sem dados.", flush=True)

            

        # 3. EXAMES
        start_sec = time.perf_counter()
        today = datetime.now()
        year_ago = today - timedelta(days=365)
        
        dados_exames_para_formatar = {}
        for titulo, dados in all_extractions.items():
            data_consulta = extract_date_from_title(titulo)
            if data_consulta >= year_ago:
                exames_filtrados = [e for e in dados.get("exames", []) if e.get("categoria") != "exame_objetivo"]
                
                if exames_filtrados:
                    dados_exames_para_formatar[titulo] = {"exames": exames_filtrados}
                    print(f"[DEBUG EXAMES] {len(exames_filtrados)} exames complementares em: {titulo}")
            

        if dados_exames_para_formatar:

            print(f"[EXAMES] Iniciado. Processando exames do último ano.", flush=True)
            text_ex = change_data_format(dados_exames_para_formatar, seccao_alvo="exames")
            if not text_ex: 
                print("[DEBUG EXAMES] change_data_format retornou vazio!")
            
            user_prompt = PROMPT_EXAMES.format(extracted_data=text_ex)
            
            schema = {"exames": list}
            fallback = {"exames": [{"nome": "Sem exames realizados no último ano", "data": "N/A", "tipo_exame": "N/A", "resultado": "N/A"}]}
            
            dados, tempo, retry = self.process_llm_section(user_prompt, "EXAMES", schema, fallback)
            
            if dados and isinstance(dados.get("exames"), list) and len(dados["exames"]) > 0:
                if dados["exames"][0].get("nome") != "Sem exames realizados no último ano":
                    sumario_consolidado_dict.update({"exames": dados["exames"]})
                            
            if retry: algum_retry = True
            tempos_seccoes["EXAMES"] = {"duration": time.perf_counter() - start_sec, "inference": tempo}
        else:
            print("[EXAMES] Ignorado: Sem exames no último ano.", flush=True)
            sumario_consolidado_dict.update({"exames": [{"nome": "N/A", "data": "N/A", "tipo_exame": "N/A", "resultado": "Sem exames registados no último ano."}]})
            tempos_seccoes["EXAMES"] = {"duration": time.perf_counter() - start_sec, "inference": 0.0}




        # 4. PLANO TERAPÊUTICO
        start_sec = time.perf_counter()
        today = datetime.now()
        year_ago = today - timedelta(days=365)
        
        planos_por_especialidade = {}
        dados_para_formatar = {}

        for titulo, dados in all_extractions.items():
            data_consulta = extract_date_from_title(titulo)
            if data_consulta < year_ago: continue
            
            # Normalização estrita: apenas letras e números, minúsculas
            esp_raw = titulo.split(" - ")[0].strip()
            esp_key = re.sub(r'[^a-zA-Z0-9]', '', esp_raw).lower()
            
            # Verifica se já existe, se a data for mais recente, substitui
            if esp_key not in planos_por_especialidade or data_consulta > planos_por_especialidade[esp_key]['data']:
                planos_por_especialidade[esp_key] = {'data': data_consulta, 'titulo': titulo}
                
        # Agora, apenas os títulos selecionados vão para o formatador
        for esp_key, info in planos_por_especialidade.items():
            titulo_selecionado = info['titulo']
            dados_para_formatar[titulo_selecionado] = all_extractions[titulo_selecionado]

        text_pl_combined = change_data_format(dados_para_formatar, seccao_alvo="plano")

        if text_pl_combined.strip():
            user_prompt = PROMPT_PLANO.format(extracted_data=text_pl_combined.strip())
            
            schema = {"plano": list}
            fallback = {"plano": [{"especialidade": "N/A", "data": "N/A", "conteudo": "Erro ao gerar plano."}]}
            
            dados, tempo, retry = self.process_llm_section(user_prompt, "PLANO", schema, fallback)
            sumario_consolidado_dict.update(dados)

            if retry: 
                algum_retry = True
            tempos_seccoes["PLANO"] = {"duration": time.perf_counter() - start_sec, "inference": tempo}

      
        
        summary_final_limpo = json.dumps(sumario_consolidado_dict, ensure_ascii=False)
        total_llm = sum(sec["inference"] for sec in tempos_seccoes.values())

        print(f"\n[DEBUG METRICA] Tempo REAL global de sumarização: {time.perf_counter() - start_global:.2f}s")
        print(f"[DEBUG METRICA] Tempo LLM somado: {total_llm:.2f}s")

        return summary_final_limpo.strip(), tempos_seccoes, algum_retry