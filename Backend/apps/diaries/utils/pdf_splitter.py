import os
import sys
import fitz  # PyMuPDF
import pytesseract
import io
import re 

from PIL import Image
from pathlib import Path

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

#caminho_tesseract = os.getenv('TESSERACT_PATH', 'tesseract')
#pytesseract.pytesseract.tesseract_cmd = caminho_tesseract

from Pipeline.llm import chat


SYS_PROMPT_PRE_CLEAN = """A tua ÚNICA tarefa é TRANSCREVER o texto fornecido, linha a linha, limpando o lixo do hospital, mas mantendo a informação médica e a identificação das consultas intocáveis, na sua exata ordem original.

REGRAS DE CÓPIA E ORDEM (O QUE MANTER OBRIGATORIAMENTE):
1. CABEÇALHO DA CONSULTA E TAG (CRÍTICO): Se o texto clínico de uma consulta COMEÇAR com a linha do Médico/Data, escreve "[NOVO DIARIO]" na linha imediatamente acima, e depois copia essa linha da Data/Médico.
2. TEXTO CLÍNICO E CONTINUAÇÕES: Se uma página começar com lixo institucional e o texto que se segue for uma continuação (ex: análises, sintomas), transcreve esse texto clínico imediatamente sem inventar a tag "[NOVO DIARIO]". Não movas o texto de sítio!
3. ASSINATURAS NOS DIAGNÓSTICOS (FALSOS POSITIVOS): Se aparecer uma linha com Médico e Data mais para o final do texto (por exemplo, nas secções "Diagnósticos" ou "Notas de Enfermagem"), isso é uma mera assinatura. NÃO CRIES a tag "[NOVO DIARIO]" aí. Limita-te a transcrever essa linha exatamente no local onde ela aparece.

O QUE OMITIR (APAGAR APENAS ESTE LIXO):
- "Processado por computador - SClínico" e a paginação (ex: "Pag. 1/2"), mesmo que apareça colada a outras palavras (ex: "Pag. 1/2O UNIDADE LOCAL...").
- A frase "UNIDADE LOCAL DE SAÚDE", moradas e códigos numéricos soltos com asteriscos ou símbolos (ex: *1111111* ou *9399484 +).
- O Nome do Doente e a linha demográfica ("Masculino" ou "Feminino - Dta Nasc..."). 
- As palavras exatas "Diário Clínico" e "Consulta Externa".

Abaixo tens 4 EXEMPLOS de como deves atuar (NÃO COPIES OS DADOS DELES):

--- EXEMPLO 1: INÍCIO DE UM NOVO DIÁRIO ---
Texto recebido:
15-10-2025 09:50 Dr(a). Falso (HUC-NEUROLOGIA)
* doença de Parkinson

O que devolves:
[NOVO DIARIO]
15-10-2025 09:50 Dr(a). Falso (HUC-NEUROLOGIA)
* doença de Parkinson

--- EXEMPLO 2: PÁGINA DE CONTINUAÇÃO (SEM MÉDICO) ---
Texto recebido:
Processado por computador - SClínico
Pag. 2/2
UNIDADE LOCAL DE SAÚDE | Doente Falso
Diário Clínico
Consulta Externa
TA 112/51 mmHg
reformulo medicação.

O que devolves:
TA 112/51 mmHg
reformulo medicação.

--- EXEMPLO 3: PÁGINA MISTA (CONTINUAÇÃO + ASSINATURA EM DIAGNÓSTICOS) ---
Texto recebido:
Processado por computador - SClínico
Pag. 3/3
UNIDADE LOCAL DE SAÚDE | Doente Falso
Diário Clínico
Consulta Externa
- glic 340; cetonémia 3.2
Contexto de vómitos a contribuir para valor.
Notas de Enfermagem
Diagnósticos
Dr(a). Falso Prior 10-08-2023
(K8000) - Litíase vesícula biliar, c/colecistite aguda

O que devolves:
- glic 340; cetonémia 3.2
Contexto de vómitos a contribuir para valor.
Notas de Enfermagem
Diagnósticos
Dr(a). Falso Prior 10-08-2023
(K8000) - Litíase vesícula biliar, c/colecistite aguda

--- EXEMPLO 4: PÁGINA DE CONTINUAÇÃO COM LIXO OCR AGLUTINADO ---
Texto recebido:
Processado por computador - SClínico
Pag. 1/2O UNIDADE LOCAL DE SAÚDE | Nome Doente Falso
COIMBRA Feminino — Dta Nasc: 1938-10-10 (87 anos)
URB PANORAMA LTE 6- 3 DTO
3000 - COIMBRA
*9399484 +
Diário Clínico
Consulta Externa
TA 112/51 mmHg
reformulo:
Madopar 200 1/2 3id

O que devolves:
TA 112/51 mmHg
reformulo:
Madopar 200 1/2 3id

AGORA É A TUA VEZ. Transcreve o texto aplicando esta lógica de ordem cronológica absoluta.
Devolve APENAS o resultado final limpo, mantendo a estrutura de linhas.
"""


def clean_clinical_text(text):
   
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    text = "\n".join([line.strip() for line in text.split('\n')])
    text = re.sub(r'([^a-zA-Z0-9\s])\1+', r'\1', text)    
    
    return text.strip()


def extract_full_pdf_text(pdf_path, client_llm, debug=True):
    """
    Extrai o texto por página, aplica OCR se necessário e submete cada página à LLM. Retorna uma string única.
    """
    paginas_processadas = []
    
    try:
        doc = fitz.open(pdf_path)
        total_paginas = len(doc)

        for page_num, page in enumerate(doc):
            width, height = page.rect.width, page.rect.height
            interest_area = fitz.Rect(0, height * 0.01, width, height * 0.99)
            
            page_text = page.get_text("text", clip=interest_area, sort=True)

            # Deteta se a página é um scan / imagem
            if not page_text.strip():
                if debug: 
                    print(f"[OCR] Página {page_num+1}/{total_paginas}: A processar imagem Tesseract...", flush=True)
                pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                page_text = pytesseract.image_to_string(img, lang='por')

            page_text_pre_limpo = clean_clinical_text(page_text)

            if len(page_text_pre_limpo.strip()) > 10:
                if debug: 
                    print(f"[LLM] Página {page_num+1}/{total_paginas}: A purificar e injetar marcadores...", flush=True)
                
                # Executa a limpeza fina página a página
                resposta, _, _ = chat(
                    client=client_llm, 
                    user_prompt=f"Aqui está o documento:\n\n{page_text_pre_limpo}", 
                    system_prompt=SYS_PROMPT_PRE_CLEAN
                )
                paginas_processadas.append(resposta.strip())
            
        doc.close()

    except Exception as e:
        print(f"Erro na extração integral do PDF: {e}", flush=True)

    return "\n\n".join(paginas_processadas)
