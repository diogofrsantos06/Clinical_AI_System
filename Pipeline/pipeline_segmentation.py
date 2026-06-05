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

import re

def gerar_titulo_diario(texto_diario, index):
    """Extrai a data e a especialidade do texto bruto para criar o título."""
    primeira_linha = texto_diario.split('\n')[0].strip()
    
    # 1. Extrair a Data (Apanha tanto '10-Ago-2023' como '04-12-2025')
    match_data = re.search(r'\d{1,2}[-/](?:[A-Za-z]{3}|\d{1,2})[-/]\d{2,4}', primeira_linha)
    data = match_data.group(0) if match_data else "Data Desconhecida"
    
    # Padronizar a data: se estiver em formato "04-12-2025", converte para "04-Dez-2025"
    if re.match(r'\d{2}-\d{2}-\d{4}', data):
        meses = {
            '01':'Jan', '02':'Fev', '03':'Mar', '04':'Abr', '05':'Mai', '06':'Jun', 
            '07':'Jul', '08':'Ago', '09':'Set', '10':'Out', '11':'Nov', '12':'Dez'
        }
        partes = data.split('-')
        if len(partes) == 3:
            dia, mes, ano = partes
            data = f"{dia}-{meses.get(mes, mes)}-{ano}"
    
    # 2. Extrair a Especialidade
    if '/' in primeira_linha:
        # Formato 1: "... / HUC-URG CIRURGIA GERAL"
        especialidade = primeira_linha.split('/')[-1].strip()
        
    elif '(' in primeira_linha and ')' in primeira_linha:
        # Formato 2: "... (HUC-ONCOLOGIA MEDICA)"
        # Procura o texto dentro do último par de parênteses da linha
        match_especialidade = re.search(r'\(([^)]+)\)[^()]*$', primeira_linha)
        if match_especialidade:
            especialidade = match_especialidade.group(1).strip()
        else:
            especialidade = f"Nota Clínica {index}"
            
    else:
        # Fallback (Plano B) se não encontrar nem barra nem parênteses
        especialidade = f"Nota Clínica {index}" 
        
    return f"{especialidade} - {data}"

def get_diary_start_indices(text):
    
    #Identifica o início de cada diário. 
    date_part = r'\d{1,2}[-/](?:[A-Za-z]{3}|\d{1,2})[-/]\d{2,4}'
    time_part = r'(?:\s+\d{2}:\d{2}(?::\d{2})?)?'
    doctor_part = r'.*?(?:Dr\(?a?\)?\.?\s|Drª\s|Médico:)' 
    
    full_pattern = f'{date_part}{time_part}{doctor_part}'
    return [m.start() for m in re.finditer(full_pattern, text, re.IGNORECASE)]


def run_smart_segmentation(full_text, client):
    indices = get_diary_start_indices(full_text)

    print(f"\n[DEBUG] Regex encontrou {len(indices)} inícios de diários no PDF.", flush=True)

    if not indices:
        print("[AVISO] Nenhum diário encontrado pelo Regex! A extração vai parar aqui.", flush=True)
        return []
    
    indices.append(len(full_text))
    todos_diarios = []
    total_esperado = len(indices) - 1

    for i in range(len(indices) - 1):
        inicio = indices[i]
        fim = indices[i+1]
        segmento_bruto = full_text[inicio:fim].strip()
        
        if len(segmento_bruto) < 20: 
            print(f"[{i+1}/{total_esperado}] Ignorado: Segmento muito curto ({len(segmento_bruto)} caracteres).", flush=True)
            continue

        # Identificamos se é o último bloco para aplicar a regra restritiva
        e_ultimo = (i == len(indices) - 2)

        print(f"[{i+1}/{total_esperado}] A enviar para o LLM (Tamanho: {len(segmento_bruto)} caracteres)...", flush=True)

        if e_ultimo:
            regra_extra = """
        3. ATENÇÃO: Este é o último bloco do documento e contém secções extra.
           - DEVES REMOVER completamente as secções: "Notas de Enfermagem", "Medicação", "MCDT Requisitados" e "Destino do Doente".
           - DEVES MANTER a secção "Diagnósticos" (ou "Diagnosticos") e o seu respetivo conteúdo. Adiciona esta secção no final da tua resposta, logo após o fim da narrativa do médico.
            """
        else:
            regra_extra = ""

        sys_prompt = f"""
        És um assistente médico. O teu objetivo é LIMPAR esta nota clínica.
        1. Mantém conteúdo clínico, datas e nomes de médicos.
        2. Remove lixo de formatação (cabeçalhos, rodapés).{regra_extra}
        4. Devolve apenas o texto limpo, sem comentários.
        """
        
        try:
            resposta, tempo_llm, houve_retry = chat(client, user_prompt=segmento_bruto, system_prompt=sys_prompt)
            if len(resposta.strip()) > 10:
                titulo_gerado = gerar_titulo_diario(segmento_bruto, i+1)
                
                diario_obj = {
                    "titulo": titulo_gerado,
                    "texto": resposta.strip()
                }
                
                todos_diarios.append(diario_obj)
                print(f"[{i+1}/{total_esperado}] Sucesso! Título: {titulo_gerado}", flush=True)
            else:
                print(f"[{i+1}/{total_esperado}] Falhou: LLM devolveu vazio.", flush=True)
                
            # 2. PREVENÇÃO DE RATE LIMITS DA GROQ
            time.sleep(1.5) 
            
        except Exception as e:
            # 3. DEBUG CRÍTICO DO ERRO
            print(f"\n!!! ERRO CRÍTICO NO DIÁRIO {i+1} !!!", flush=True)
            print(f"Mensagem: {str(e)}", flush=True)
            print(traceback.format_exc(), flush=True)
            
            # Se for um erro de Rate Limit, esperamos uns segundos antes de continuar
            if "rate_limit" in str(e).lower() or "429" in str(e):
                print(">> Limite da Groq atingido! A esperar 10 segundos antes do próximo...", flush=True)
                time.sleep(10)

    return todos_diarios
