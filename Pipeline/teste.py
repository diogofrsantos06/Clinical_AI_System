import os
import sys
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
from pathlib import Path

# Garante que o Python consegue encontrar o teu ficheiro llm.py
BASE_DIR = Path(__file__).resolve().parent  
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# Importa as tuas funções
from llm import chat, get_client

# Configuração do Tesseract (Ajusta o caminho se necessário)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ==========================================
# FUNÇÕES DE LIMPEZA E EXTRAÇÃO
# ==========================================

def clean_clinical_text(text):
    """Limpa o texto extraído para otimizar o processamento da LLM."""
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    text = "\n".join([line.strip() for line in text.split('\n')])
    text = re.sub(r'([^a-zA-Z0-9\s])\1+', r'\1', text)    
    return text.strip()

def extrair_texto_com_ocr(caminho):
    """Lê o PDF, aplica OCR se a página for uma imagem, e limpa o conteúdo página a página."""
    print(f"A abrir o PDF: {caminho}...")
    texto_por_pagina = []
    
    try:
        doc = fitz.open(caminho)
        
        for page_num, page in enumerate(doc):
            width, height = page.rect.width, page.rect.height
            interest_area = fitz.Rect(0, height * 0.01, width, height * 0.99)
            
            page_text = page.get_text("text", clip=interest_area, sort=True)

            # Se a página não tiver texto (scan), dispara o OCR
            if not page_text.strip():
                print(f"Página {page_num+1}: Texto não detetado. A iniciar OCR (Tesseract)...")
                pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                page_text = pytesseract.image_to_string(img, lang='por')
            
            # Limpa ruído do OCR
            page_text_limpo = clean_clinical_text(page_text)
            texto_por_pagina.append(page_text_limpo)

        doc.close()

        ficheiro_saida = "resultado_OCR.txt"
        with open(ficheiro_saida, "w", encoding="utf-8") as f:
            f.write("".join(texto_por_pagina))

        return texto_por_pagina

    except Exception as e:
        print(f"Erro na extração do PDF: {e}")
        return []

# ==========================================
# EXECUÇÃO DO TESTE
# ==========================================

if __name__ == "__main__":
    
    # 1. CAMINHO DO PDF
    CAMINHO_PDF = r"C:\Users\Utilizador\Desktop\00.pdf"
    
    if not os.path.exists(CAMINHO_PDF):
        print(f"ERRO: O ficheiro não foi encontrado em {CAMINHO_PDF}")
        exit()

    # 2. INICIALIZAÇÃO
    client = get_client()
    paginas_brutas = extrair_texto_com_ocr(CAMINHO_PDF)
    
    print(f"PDF carregado! Contém {len(paginas_brutas)} páginas.\n")

    texto_final_limpo = []
    tempo_total = 0.0

    # 3. PROMPT DE LIMPEZA
    sys_prompt = """A tua ÚNICA tarefa é TRANSCREVER o texto fornecido, linha a linha, limpando o lixo do hospital, mas mantendo a informação médica e a identificação das consultas intocáveis, na sua exata ordem original.

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

    # 4. PROCESSAMENTO PÁGINA A PÁGINA
    for i, texto_pagina in enumerate(paginas_brutas, 1):
        
        if len(texto_pagina.strip()) < 10:
            print(f"[{i}/{len(paginas_brutas)}] Página ignorada (muito curta/vazia mesmo após OCR).")
            continue

        print(f"[{i}/{len(paginas_brutas)}] A limpar página com a LLM...", end=" ", flush=True)
        
        # Envolvemos o texto para a IA perceber claramente onde começa e acaba
        prompt_utilizador = f"Aqui está o documento:\n\n{texto_pagina}"

        resposta, tempo_llm, _ = chat(
            client=client, 
            user_prompt=prompt_utilizador, 
            system_prompt=sys_prompt
        )
        
        tempo_total += tempo_llm
        print(f"(Demorou {tempo_llm:.2f}s)")
        
        texto_final_limpo.append(resposta.strip())

    # 5. GUARDAR RESULTADO
    ficheiro_saida = "resultado_teste_extracao.txt"
    with open(ficheiro_saida, "w", encoding="utf-8") as f:
        f.write("\n\n".join(texto_final_limpo))

    print(f"\nProcesso concluído em {tempo_total:.2f}s totais de inferência IA!")
    print(f"Verifica o ficheiro: {ficheiro_saida}")