import re
import json
import sys
import traceback
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  
PROJ_ROOT = BASE_DIR.parent                 

if str(PROJ_ROOT) not in sys.path:
    sys.path.append(str(PROJ_ROOT))
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from llm import chat


def gerar_titulo_diario(texto_diario, index):
    """Extrai a data e a especialidade do cabeçalho limpo para gerar o título."""
    linhas = [l.strip() for l in texto_diario.split('\n') if l.strip()]
    if not linhas:
        return f"Nota Clínica {index}"
        
    primeira_linha = linhas[0]
    
    # Extrair a Data
    match_data = re.search(r'\d{1,2}[-/](?:[A-Za-z]{3}|\d{1,2})[-/]\d{2,4}', primeira_linha)
    data = match_data.group(0) if match_data else "Data Desconhecida"
    
    if re.match(r'\d{2}-\d{2}-\d{4}', data):
        meses = {
            '01':'Jan', '02':'Fev', '03':'Mar', '04':'Abr', '05':'Mai', '06':'Jun', 
            '07':'Jul', '08':'Ago', '09':'Set', '10':'Out', '11':'Nov', '12':'Dez'
        }
        partes = data.split('-')
        if len(partes) == 3:
            dia, mes, ano = partes
            data = f"{dia}-{meses.get(mes, mes)}-{ano}"
    
    # Extrair a Especialidade
    if '/' in primeira_linha:
        especialidade = primeira_linha.split('/')[-1].strip()
    elif '(' in primeira_linha and ')' in primeira_linha:
        match_especialidade = re.search(r'\(([^)]+)\)[^()]*$', primeira_linha)
        especialidade = match_especialidade.group(1).strip() if match_especialidade else f"Nota Clínica {index}"
    else:
        especialidade = f"Nota Clínica {index}" 
        
    return f"{especialidade} - {data}"


def run_smart_segmentation(full_text, client):
    """
    Divide o texto purificado usando o marcador universal '[NOVO DIARIO]' gerado pela Fase 1.
    """
    # Divide a string pelos marcadores injetados e remove segmentos vazios
    segmentos = [s.strip() for s in full_text.split("[NOVO DIARIO]") if s.strip()]
    
    print(f"\n[DEBUG] Pipeline identificou {len(segmentos)} diários estruturados no texto limpo.", flush=True)
    
    todos_diarios = []
    total_esperado = len(segmentos)

    for i, segmento_bruto in enumerate(segmentos):
        
        if len(segmento_bruto) < 20: 
            print(f"[{i+1}/{total_esperado}] Ignorado: Segmento invulgarmente curto.", flush=True)
            continue

        e_ultimo = (i == total_esperado - 1)
        print(f"[{i+1}/{total_esperado}] A aplicar regras de negócio no diário...", flush=True)

        if e_ultimo:
            # Regra especial mantida para tratar o fim do documento clínico
            regra_extra = """
        3. ATENÇÃO: Este é o último bloco do documento e contém secções extra.
           - DEVES REMOVER completamente as secções: "Notas de Enfermagem", "Medicação", "MCDT Requisitados" e "Destino do Doente".
           - DEVES MANTER a secção "Diagnósticos" (or "Diagnosticos") e o seu respetivo conteúdo. Adiciona esta secção no final da tua resposta, logo após o fim da narrativa do médico.
            """
        else:
            regra_extra = ""

        sys_prompt = f"""
        És um assistente médico especialista em curadoria de registos. O teu objetivo é a validação final desta nota clínica.
        1. Garante a integridade absoluta de todo o conteúdo clínico da consulta.
        2. Certifica-te de que nenhuma frase médica é cortada ou resumida.{regra_extra}
        4. Devolve exclusivamente o texto clínico resultante limpo, mantendo a estrutura de quebra de linhas, sem comentários ou markdown.
        """
        
        try:
            resposta, _, _ = chat(client, user_prompt=segmento_bruto, system_prompt=sys_prompt)
            
            if len(resposta.strip()) > 10:
                titulo_gerado = gerar_titulo_diario(segmento_bruto, i+1)
                
                diario_obj = {
                    "titulo": titulo_gerado,
                    "texto": resposta.strip()
                }
                
                todos_diarios.append(diario_obj)
                print(f"[{i+1}/{total_esperado}] Processado com Sucesso: {titulo_gerado}", flush=True)
            else:
                print(f"[{i+1}/{total_esperado}] Falhou: Resposta vazia da LLM.", flush=True)
                
            time.sleep(1.0) 
            
        except Exception as e:
            print(f"\n!!! ERRO CRÍTICO NO PROCESSAMENTO DO DIÁRIO {i+1} !!!", flush=True)
            print(traceback.format_exc(), flush=True)
            if "rate_limit" in str(e).lower() or "429" in str(e):
                time.sleep(10)

    return todos_diarios