import os, fitz, io, re, time, pytesseract

from PIL import Image, ImageEnhance, ImageOps

from Pipeline.llm import chat
    
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

#caminho_tesseract = os.getenv('TESSERACT_PATH', 'tesseract')
#pytesseract.pytesseract.tesseract_cmd = caminho_tesseract

SYS_PROMPT_PRE_CLEAN = """A tua ÚNICA tarefa é transcrever o texto fornecido, linha a linha, limpando APENAS o lixo institucional e dados pessoais, mantendo 100% da informação clínica e notas médicas intactas, na sua exata ordem original.

O texto enviado pertence a fatias de páginas de diários clínicos. Aplica as seguintes regras de limpeza cirúrgica:

--- REGRA DE ADMISSAO/URGÊNCIA (TIPO 1) ---
- Se o texto contiver a expressão 'Observações Médicas' imediatamente seguida de uma linha com Data, Hora e Médico/Serviço (ex: 'DD-Mes-AAAA HH:MM:SS Dr. ... / ...'), deves ELIMINAR TUDO o que aparece ANTES dessa linha específica no topo do texto. Esse é o início real do documento.

--- REGRA DE CABEÇALHOS E DADOS PESSOAIS (TIPO 2 - CRÍTICO) ---
- Ao longo do texto, tu vais encontrar blocos de cabeçalhos repetitivos de mudança de página. Identifica o bloco exato que COMEÇA em 'Processado por computador - SClínico' e TERMINA na expressão 'Diário Clínico Consulta Externa'.
- Deves APAGAR APENAS esse bloco de cabeçalho e todas as informações pessoais contidas DENTRO dele (Nome do paciente, morada, idade, data de nascimento, número de processo, utente, sexo, etc.).
- REGRA DE OURO (NÃO VIOLAR): A linha imediatamente a seguir à expressão 'Diário Clínico Consulta Externa' contém informação clínica importante. É ESTRITAMENTE PROIBIDO apagar ou alterar essa linha! 
- ATENÇÃO MÁXIMA: Tudo o que estiver ABAIXO ou DEPOIS da expressão 'Diário Clínico Consulta Externa' é texto clínico, relatórios, exames ou continuação do diário anterior. Deves TRANSCREVER ESSE TEXTO NA ÍNTEGRA. Nunca apagues linhas médicas, mesmo que a página não tenha um novo nome de médico ou data!

Devolve APENAS o resultado final limpo, mantendo estritamente a estrutura de linhas. Não adiciones notas, resumos ou justificações."""

def clean_clinical_text(text):
    text = re.sub(r'\n\s*\n+', '\n\n', text)    
    text = "\n".join([line.rstrip() for line in text.split('\n')])
    text = re.sub(r'([^a-zA-Z0-9\s])\1{4,}', r'\1', text)  
    return text.strip()


def extract_full_pdf_text(pdf_path, client_llm, chunk_size=4, debug=True):
    """
    Executa o OCR sequencial e usa a LLM para limpar informação de cabeçalhos e numeração de páginas
    """
    paginas_brutas = []
    metricas_recolhidas = []

    try:
        start_global = time.perf_counter()
        if debug: 
            print(f"\nExecutando OCR em todas as páginas...", flush=True)

        doc = fitz.open(pdf_path)
        total_paginas = len(doc)

        for idx in range(total_paginas):
            start_p = time.perf_counter()
            page = doc[idx]
            
            matrix = fitz.Matrix(300/72, 300/72)
            pix = page.get_pixmap(matrix=matrix)
            
            img = Image.open(io.BytesIO(pix.tobytes("png"))).convert('L')
            img = ImageEnhance.Contrast(img).enhance(2.0)
            img = ImageOps.autocontrast(img)
            
            custom_config = r'--psm 4 --oem 1 -c preserve_interword_spaces=1'
            texto_bruto_ocr = pytesseract.image_to_string(img, lang='por', config=custom_config)
            texto_pre_limpo = clean_clinical_text(texto_bruto_ocr)
            
            paginas_brutas.append(texto_pre_limpo)

            duracao_ocr = time.perf_counter() - start_p
            
            metricas_recolhidas.append({
                "operation_type": "OCR_PAGE",
                "section_name": f"Página {idx+1}",
                "duration_seconds": duracao_ocr,
                "inference_duration": 0.0, 
                "input_size": len(texto_pre_limpo),
                "is_retry": False
            })

            if debug: 
                print(f"[OCR] Página {idx+1}/{total_paginas} processada em {time.perf_counter() - start_p:.2f}s", flush=True)
        
        doc.close()

        if debug: 
            print(f"\nProcessando blocos de {chunk_size} páginas sequencialmente na LLM...", flush=True)

        blocos_limpos = []
        
        for i in range(0, total_paginas, chunk_size):
            start_chunk = time.perf_counter()
            bloco_paginas = paginas_brutas[i:i + chunk_size]
            texto_do_chunk = "\n\n".join(bloco_paginas)

            if debug: 
                print(f"Enviando Bloco: Páginas {i+1} até {min(i + chunk_size, total_paginas)}...", flush=True)
            
            max_tentativas = 3
            texto_bloco_limpo = texto_do_chunk 
            houve_retry = False
            
            for tentativa in range(1, max_tentativas + 1):
                try:
                    resultado_chat = chat(
                        client=client_llm, 
                        user_prompt=f"Aqui está o bloco de páginas para limpar:\n\n{texto_do_chunk}", 
                        system_prompt=SYS_PROMPT_PRE_CLEAN
                    )
                    
                    resposta_texto = resultado_chat[0] if isinstance(resultado_chat, (tuple, list)) else str(resultado_chat)
                    
                    if "504 Server Error" in resposta_texto or "Gateway Timeout" in resposta_texto:
                        raise ValueError("A LLM devolveu um erro de Timeout disfarçado de texto.")
                        
                    texto_bloco_limpo = resposta_texto.strip()
                    houve_retry = (tentativa > 1)
                    break # Sucesso!
                    
                except Exception as e:
                    print(f"[LLM PRE-CLEAN] Falha na tentativa {tentativa}/{max_tentativas}: {str(e)}", flush=True)
                    if tentativa < max_tentativas:
                        print("[LLM PRE-CLEAN] A aguardar 5 segundos...", flush=True)
                        time.sleep(5)
                    else:
                        print("[LLM PRE-CLEAN] Limite atingido! A devolver o texto OCR bruto para evitar perda de dados.", flush=True)
                        houve_retry = True
            
            duracao_chunk = time.perf_counter() - start_chunk
            
            metricas_recolhidas.append({
                "operation_type": "PRE_CLEAN_CHUNK",
                "section_name": f"Bloco {int(i/chunk_size)+1}",
                "duration_seconds": duracao_chunk,
                "inference_duration": duracao_chunk, 
                "input_size": len(texto_do_chunk),
                "is_retry": houve_retry
            })
            
            if texto_bloco_limpo:
                blocos_limpos.append(texto_bloco_limpo)

        texto_total_limpo = "\n\n".join(blocos_limpos)
        
        if debug: print(f"\nFASE EXTRAÇÃO DOS DIÁRIOS CONCLUÍDA COM SUCESSO EM {time.perf_counter() - start_global:.2f}s!")
        return texto_total_limpo, metricas_recolhidas

    except Exception as e:
        print(f"Erro crítico no pipeline de extração de texto: {e}", flush=True)
        return ""