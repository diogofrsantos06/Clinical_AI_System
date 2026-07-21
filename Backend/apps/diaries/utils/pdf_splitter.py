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
    """Runs OCR page-by-page, then uses the LLM to strip repeated headers/page-numbering from each chunk."""
    raw_pages = []
    collected_metrics = []

    try:
        start_global = time.perf_counter()
        if debug:
            print("\nRunning OCR on every page...", flush=True)

        doc = fitz.open(pdf_path)
        total_pages = len(doc)

        for idx in range(total_pages):
            start_page = time.perf_counter()
            page = doc[idx]

            matrix = fitz.Matrix(300/72, 300/72)
            pix = page.get_pixmap(matrix=matrix)

            img = Image.open(io.BytesIO(pix.tobytes("png"))).convert('L')
            img = ImageEnhance.Contrast(img).enhance(2.0)
            img = ImageOps.autocontrast(img)

            custom_config = r'--psm 4 --oem 1 -c preserve_interword_spaces=1'
            raw_ocr_text = pytesseract.image_to_string(img, lang='por', config=custom_config)
            pre_cleaned_text = clean_clinical_text(raw_ocr_text)

            raw_pages.append(pre_cleaned_text)

            ocr_duration = time.perf_counter() - start_page

            collected_metrics.append({
                "operation_type": "OCR_PAGE",
                "section_name": f"Página {idx+1}",
                "duration_seconds": ocr_duration,
                "inference_duration": 0.0,
                "input_size": len(pre_cleaned_text),
                "is_retry": False
            })

            if debug:
                print(f"[OCR] Page {idx+1}/{total_pages} processed in {time.perf_counter() - start_page:.2f}s", flush=True)

        doc.close()

        if debug:
            print(f"\nSending {chunk_size}-page chunks to the LLM sequentially...", flush=True)

        cleaned_chunks = []

        for i in range(0, total_pages, chunk_size):
            start_chunk = time.perf_counter()
            page_chunk = raw_pages[i:i + chunk_size]
            chunk_text = "\n\n".join(page_chunk)

            if debug:
                print(f"Sending chunk: pages {i+1} to {min(i + chunk_size, total_pages)}...", flush=True)

            max_attempts = 3
            cleaned_chunk_text = chunk_text
            had_retry = False
            chunk_stats = {}
            attempts_exhausted = False
            error_type = None

            for attempt in range(1, max_attempts + 1):
                try:
                    chunk_stats = {}
                    chat_result = chat(
                        client=client_llm,
                        user_prompt=f"Aqui está o bloco de páginas para limpar:\n\n{chunk_text}",
                        system_prompt=SYS_PROMPT_PRE_CLEAN,
                        stats_sink = chunk_stats
                    )

                    response_text = chat_result[0] if isinstance(chat_result, (tuple, list)) else str(chat_result)

                    if "504 Server Error" in response_text or "Gateway Timeout" in response_text:
                        raise ValueError("The LLM returned a timeout error disguised as text.")

                    cleaned_chunk_text = response_text.strip()
                    had_retry = (attempt > 1)
                    break  # success!

                except Exception as e:
                    print(f"[LLM PRE-CLEAN] Attempt {attempt}/{max_attempts} failed: {str(e)}", flush=True)
                    error_type = "timeout" if "Timeout" in str(e) else "network"
                    if attempt < max_attempts:
                        print("[LLM PRE-CLEAN] Waiting 5 seconds...", flush=True)
                        time.sleep(5)
                    else:
                        print("[LLM PRE-CLEAN] Retry limit reached! Falling back to the raw OCR text to avoid data loss.", flush=True)
                        had_retry = True
                        attempts_exhausted = True

            chunk_duration = time.perf_counter() - start_chunk

            collected_metrics.append({
                "operation_type": "PRE_CLEAN_CHUNK",
                "section_name": f"Bloco {int(i/chunk_size)+1}",
                "duration_seconds": chunk_duration,
                "inference_duration": chunk_duration,
                "tokens_per_second": chunk_stats.get("generation_tokens_per_second", 0.0),
                "model_ram_gb": chunk_stats.get("model_ram_gb"),
                "model_vram_gb": chunk_stats.get("model_vram_gb"),
                "prompt_tokens": chunk_stats.get("prompt_tokens"),
                "completion_tokens": chunk_stats.get("completion_tokens"),
                "finish_reason": chunk_stats.get("finish_reason"),
                "attempt_count": chunk_stats.get("attempt_count", attempt),
                "kv_cache_usage_percent": chunk_stats.get("kv_cache_usage_percent"),
                "requests_waiting": chunk_stats.get("requests_waiting"),
                "fallback_used": attempts_exhausted,
                "error_type": error_type if attempts_exhausted else None,
                "input_size": len(chunk_text),
                "is_retry": had_retry
            })

            if cleaned_chunk_text:
                cleaned_chunks.append(cleaned_chunk_text)

        full_clean_text = "\n\n".join(cleaned_chunks)

        if debug:
            print(f"\nDIARY EXTRACTION PHASE COMPLETED SUCCESSFULLY IN {time.perf_counter() - start_global:.2f}s!")
        return full_clean_text, collected_metrics

    except Exception as e:
        print(f"Critical error in text extraction pipeline: {e}", flush=True)
        return "", []
