import re
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  
PROJ_ROOT = BASE_DIR.parent                 

if str(PROJ_ROOT) not in sys.path:
    sys.path.append(str(PROJ_ROOT))
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from groq_client import get_client, chat


def get_diary_start_indices(text):
    
    #Identifica o início de cada diário. 
    date_part = r'\d{1,2}[-/](?:[A-Za-z]{3}|\d{1,2})[-/]\d{2,4}'
    time_part = r'(?:\s+\d{2}:\d{2}(?::\d{2})?)?'
    doctor_part = r'.*?(?:Dr\(?a?\)?\.?\s|Drª\s|Médico:)' 
    
    full_pattern = f'{date_part}{time_part}{doctor_part}'
    return [m.start() for m in re.finditer(full_pattern, text, re.IGNORECASE)]

def prepare_segmentation_prompt(text_block):
    num_no_bloco = len(get_diary_start_indices(text_block))
    
    system_prompt = f"""
    És um extrator de texto médico. O teu objetivo é isolar notas clínicas (diários).
    Receberás um bloco de texto que contém aproximadamente {num_no_bloco} diários.

    REGRAS:
    1. Devolve CADA diário individualmente.
    2. Usa OBRIGATORIAMENTE os marcadores [INICIO_DIARIO] e [FIM_DIARIO] para cada nota.
    3. Remove lixo (cabeçalhos de hospital, NIF, moradas, "Página X de Y").
    4. Mantém o conteúdo clínico INTEGRAL. Não resumas.
    """
    return system_prompt

def parse_segmentation_response(response_text):

    pattern = r'\[INICIO_DIARIO\](.*?)\[FIM_DIARIO\]'
    diarios = re.findall(pattern, response_text, re.DOTALL)
    
    if not diarios and len(response_text) > 50:
        print(f"Aviso: A IA respondeu mas não usou as tags [INICIO_DIARIO]. Tamanho da resposta: {len(response_text)}")
        return [response_text.strip()]
        
    return [d.strip() for d in diarios if len(d.strip()) > 10]

def run_smart_segmentation(full_text, client):
    indices = get_diary_start_indices(full_text)
    if not indices:
        return []
    
    indices.append(len(full_text))
    todos_diarios = []

    for i in range(len(indices) - 1):
        inicio = indices[i]
        fim = indices[i+1]
        segmento_bruto = full_text[inicio:fim].strip()
        
        if len(segmento_bruto) < 20: continue

        # Identificamos se é o último bloco para aplicar a regra restritiva
        e_ultimo = (i == len(indices) - 2)

        print(f"Processando Diário {i+1}...")
        
        # Prompt adaptativo
        sys_prompt = f"""
        És um assistente médico. O teu objetivo é LIMPAR esta nota clínica.
        1. Mantém conteúdo clínico, datas e nomes de médicos.
        2. Remove lixo de formatação (cabeçalhos, rodapés).
        { '3. ATENÇÃO: Se o texto terminar com secções de "Notas de Enfermagem", "Diagnósticos", "Medicação", "MCDT Requisitados" e "Destino do Doente", REMOVE-AS. Para apenas no fim da narrativa do médico.' if e_ultimo else '' }
        4. Devolve apenas o texto limpo, sem comentários.
        """
        
        try:
            resposta = chat(client, user_prompt=segmento_bruto, system_prompt=sys_prompt)
            if len(resposta.strip()) > 10:
                todos_diarios.append(resposta.strip())
        except Exception as e:
            print(f"Erro no diário {i+1}: {e}")

    return todos_diarios

'''
from Backend.apps.diaries.utils.pdf_splitter import extract_full_pdf_text

if __name__ == "__main__":
    PDF_TESTE = r"C:/Users/Utilizador/Desktop/01.pdf"
    
    print("\n[PASSO 1] Extraindo texto do PDF...")
    resultado_pdf = extract_full_pdf_text(PDF_TESTE, debug=False)
    texto_total = resultado_pdf[0] if isinstance(resultado_pdf, tuple) else resultado_pdf

    if not texto_total:
        print("Erro: Não foi possível extrair texto do PDF.")
        sys.exit()
    
    client_groq = get_client()
    lista_final_diarios = run_smart_segmentation(texto_total, client_groq)

    print(f"RESULTADO: {len(lista_final_diarios)} diários processados.")

    for idx, d in enumerate(lista_final_diarios, 1):
        tamanho = len(d)
        print(f"\nDIÁRIO {idx} | Total de Caracteres: {tamanho}")
        print({d}) 
        '''

#Correr python Pipeline/pipeline_segmentation.py na diretoria raiz do projeto.