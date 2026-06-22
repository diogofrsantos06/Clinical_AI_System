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

    def generate_summary(self, all_extractions: Dict[str, Any]) -> tuple:
        if not all_extractions:
            return "Nenhum dado disponível para sumarização.", 0.0, False

        print("\n" + "-"*30 + " INÍCIO DA SUMARIZAÇÃO " + "-"*30)
        sumario_consolidado_dict = {}
        
        def executar_antecedentes():
            start_time = time.perf_counter()
            text = change_data_format(all_extractions, seccao_alvo="diagnosticos")

            if text:
                print(f"[ANTECEDENTES] Iniciado! Tamanho do input: {len(text)} caracteres.", flush=True)

                user_prompt = PROMPT_ANTECEDENTES.format(extracted_data=text)
                res = chat(self.client, user_prompt, self.system_prompt)

                print(f"[ANTECEDENTES] Terminou em {time.perf_counter() - start_time:.2f}s", flush=True)
                return res
            
            print("[ANTECEDENTES] Ignorado: Sem dados de diagnósticos.", flush=True)
            return None

        def executar_medicacao():
            start_time = time.perf_counter()
            text_med = change_data_format(all_extractions, seccao_alvo="medicacao")
            text_alergias = change_data_format(all_extractions, seccao_alvo="alergias")

            text_med_alergias = f"{text_med}\n\n{text_alergias}".strip()

            if text_med_alergias:
                print(f"[MEDICAÇÃO/ALERGIAS] Iniciado! Tamanho do input: {len(text_med_alergias)} caracteres.", flush=True)
                
                user_prompt = PROMPT_MEDICACAO.format(extracted_data=text_med_alergias)
                res = chat(self.client, user_prompt, self.system_prompt)
                
                print(f"[MEDICAÇÃO/ALERGIAS] Terminou em {time.perf_counter() - start_time:.2f}s", flush=True)
                return res
            
            print("[MEDICAÇÃO/ALERGIAS] Cancelado: Sem dados de medicação/alergias.", flush=True)
            return None

        def executar_exames():
            start_time = time.perf_counter()
            text = change_data_format(all_extractions, seccao_alvo="exames")

            if text:
                print(f"[EXAMES] Iniciado! Tamanho do input: {len(text)} caracteres.", flush=True)
                
                user_prompt = PROMPT_EXAMES.format(extracted_data=text)
                res = chat(self.client, user_prompt, self.system_prompt)
                
                print(f"[EXAMES] Terminou em {time.perf_counter() - start_time:.2f}s", flush=True)
                return res
            
            print("[EXAMES] Ignorado: Sem dados de exames.", flush=True)
            return None

        def executar_plano():
            start_time = time.perf_counter()
            ultimo_titulo = list(all_extractions.keys())[-1]
            ultimo_conteudo = all_extractions[ultimo_titulo]
            payload_recente = {ultimo_titulo: ultimo_conteudo}

            text = change_data_format(payload_recente, seccao_alvo="plano")
            
            if text:
                print(f"[PLANO] Iniciado! Focado apenas no diário: '{ultimo_titulo}'.", flush=True)
                
                user_prompt = PROMPT_PLANO.format(extracted_data=text)
                res = chat(self.client, user_prompt, self.system_prompt)
                
                print(f"[PLANO] Terminou em {time.perf_counter() - start_time:.2f}s", flush=True)
                return res
            
            print("[PLANO] Ignorado: Sem dados de plano.", flush=True)
            return None

        # Disparar as 4 chamadas simultaneamente para a API/Ollama
        total_tempo_llm = 0.0
        algum_retry = False
        start_global = time.perf_counter()

        res_ant = executar_antecedentes()
        res_med = executar_medicacao()
        res_ex = executar_exames()
        res_pl = executar_plano()
        
        tempo_total_real = time.perf_counter() - start_global
        print(f"\n[DEBUG METRICA] Tempo REAL de espera do utilizador (Sequencial): {tempo_total_real:.2f}s")

        mapeamento_resultados = [
            (res_ant, "Antecedentes"),
            (res_med, "Medicação"),
            (res_ex, "Exames"),
            (res_pl, "Plano")
        ]

        print("\n" + "-"*20 + " PROCESSANDO RESPOSTAS JSON " + "-"*20)

        for res, nome_fase in mapeamento_resultados:
            if res:
                summary, tempo, retry = res
                total_tempo_llm += tempo 
                
                if retry: 
                    algum_retry = True
                
                match = re.search(r'\{.*\}', summary, re.DOTALL)

                if match:
                    try:
                        json_puro = match.group(0)
                        dados_fase = json.loads(json_puro)
                        sumario_consolidado_dict.update(dados_fase)

                        print(f"[{nome_fase}] JSON válido decodificado e fundido com sucesso. (Inferência isolada: {tempo:.2f}s)")
                    
                    except Exception as e:
                        print(f"[{nome_fase}] ERRO DE PARSE! Detalhe: {e}")
                        print(f"--- CONTEÚDO BRUTO DO ERRO ({nome_fase}) ---\n{summary}\n---")
                else:
                    print(f"[{nome_fase}] ERRO! Nenhum padrão JSON '{{ ... }}' foi encontrado na resposta.")

        summary_final_limpo = json.dumps(sumario_consolidado_dict, ensure_ascii=False)
        print(f"[DEBUG METRICA] Tempo total de processamento sequencial somado: {total_tempo_llm:.2f}s")
        print("-"*30 + "\n")

        return summary_final_limpo.strip(), total_tempo_llm, algum_retry

