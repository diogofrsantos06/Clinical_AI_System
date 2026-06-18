import os
import fitz  # PyMuPDF
import pytesseract
import io
import re 
import time

from PIL import Image

from concurrent.futures import ThreadPoolExecutor 

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
    Executa o OCR sequencial em baixa resolução (leve em RAM/ultra rápido) 
    e paraleliza apenas as chamadas à LLM para evitar o erro SIGKILL (Out Of Memory).
    """
    paginas_brutas = []

    try:
        start_ocr_global = time.perf_counter()
        doc = fitz.open(pdf_path)
        total_paginas = len(doc)
        
        print(f"\n[OCR SEGURO] Iniciando leitura local de {total_paginas} páginas...", flush=True)
        
        for page_num, page in enumerate(doc):
            start_p = time.perf_counter()
            
            pix = page.get_pixmap(matrix=fitz.Matrix(150/72, 150/72))
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            
            page_text_ocr = pytesseract.image_to_string(img, lang='por')
            texto_pre_limpo = clean_clinical_text(page_text_ocr)
            
            paginas_brutas.append((page_num, texto_pre_limpo))
            
            if debug:
                print(f"[OCR Local] Página {page_num+1}/{total_paginas} lida em {time.perf_counter() - start_p:.2f}s", flush=True)
                
        doc.close()
        print(f"[OCR SEGURO] Fim do OCR de todas as páginas. Tempo total: {time.perf_counter() - start_ocr_global:.2f}s")

        def refinar_pagina_llm(par_pagina):
            num, texto_bruto = par_pagina
            if len(texto_bruto.strip()) > 10:
                if debug: print(f"[THREAD-LLM] Refinando página {num+1}/{total_paginas}...", flush=True)
                
                resposta, _, _ = chat(
                    client=client_llm, 
                    user_prompt=f"Aqui está o documento:\n\n{texto_bruto}", 
                    system_prompt=SYS_PROMPT_PRE_CLEAN
                )
                return num, resposta.strip()
            return num, ""

        paginas_limpas_resultado = {}
        LIMITE_SEGURO_WORKERS = 4
        workers_finais = min(total_paginas, LIMITE_SEGURO_WORKERS)
        
        print(f"\n[LLM PARALELO] Enviando as páginas em simultâneo para o modelo quente...", flush=True)
        with ThreadPoolExecutor(max_workers=workers_finais) as executor:
            resultados = executor.map(refinar_pagina_llm, paginas_brutas)
            
            for num, texto_final in resultados:
                paginas_limpas_resultado[num] = texto_final

        paginas_ordenadas = []
        for num in sorted(paginas_limpas_resultado.keys()):
            if paginas_limpas_resultado[num]:
                paginas_ordenadas.append(paginas_limpas_resultado[num])

        return "\n\n".join(paginas_ordenadas)

    except Exception as e:
        print(f"Erro crítico no pipeline de extração de texto: {e}", flush=True)
        return ""