import re, sys, time
from pathlib import Path
from datetime import date

from Pipeline.llm import chat

BASE_DIR = Path(__file__).resolve().parent  
PROJ_ROOT = BASE_DIR.parent                 

if str(PROJ_ROOT) not in sys.path:
    sys.path.append(str(PROJ_ROOT))
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

DATE_PART = r'\d{1,2}[-/](?:[A-Za-z]{3}|\d{1,2})[-/]\d{2,4}'
TIME_PART = r'(?:\s+\d{2}:\d{2}(?::\d{2})?)?'
DOCTOR_PART = r'.*?(?:Dr\(?a?\)?\.?\s|Médico:)'

MONTHS_PT = {
    '01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr', '05': 'Mai', '06': 'Jun',
    '07': 'Jul', '08': 'Ago', '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'
}
MONTHS_PT_TO_NUM = {name.lower(): int(num) for num, name in MONTHS_PT.items()}

def parse_diary_date(date_str):
    """Parses '18-03-2026' or '18-Mar-2026' (day-month-year, 4-digit year) into a date object."""

    match = re.match(r'(\d{1,2})[-/]([A-Za-z]{3}|\d{1,2})[-/](\d{4})', date_str)
    if not match:
        return None

    day, month_str, year = match.groups()
    month = int(month_str) if month_str.isdigit() else MONTHS_PT_TO_NUM.get(month_str.lower())
    if not month:
        return None

    try:
        return date(int(year), month, int(day))
    except ValueError:
        return None
    
def build_diary_title(diary_text, index):
    """Derives a short title (specialty + date) from a diary's header line."""
    if not diary_text or not diary_text.strip():
        return f"Nota_Clinica_{index}"

    header_pattern = fr'{DATE_PART}{TIME_PART}{DOCTOR_PART}[^\n]*'
    header_match = re.search(header_pattern, diary_text, re.IGNORECASE)

    if not header_match:
        lines = [l.strip() for l in diary_text.split('\n') if l.strip()]
        if not lines:
            return f"Nota_Clinica_{index}"
        header_line = lines[0]
    else:
        header_line = header_match.group(0).strip()

    date_match = re.search(DATE_PART, header_line)
    raw_date = date_match.group(0) if date_match else None
    visit_date = parse_diary_date(raw_date) if raw_date else None
    date_str = raw_date if raw_date else "Data_Desconhecida"

    if re.match(r'\d{2}-\d{2}-\d{4}', date_str):
        day, month, year = date_str.split('-')
        date_str = f"{day}-{MONTHS_PT.get(month, month)}-{year}"

    specialty = ""
    if '/' in header_line:
        specialty = header_line.split('/')[-1].strip()
    elif '(' in header_line and ')' in header_line:
        parens_match = re.search(r'\(([^)]+)\)[^()]*$', header_line)
        if parens_match:
            specialty = parens_match.group(1).strip()

    specialty = re.sub(r'[\\/*?:"<>|.,;()]', '', specialty).strip()
    specialty = re.sub(r'\s+', '_', specialty)

    return f"{specialty} - {date_str}", visit_date


def get_diary_start_indices(text):
    """Maps the start index of every clinical record found via the doctor/date header pattern."""
    full_pattern = f'{DATE_PART}{TIME_PART}{DOCTOR_PART}'
    return [m.start() for m in re.finditer(full_pattern, text, re.IGNORECASE)]


def run_smart_segmentation(full_text, client):
    """
    Splits the OCR'd document into individual diaries using regex-based boundaries.
    Only the last block goes through the LLM, and only if it looks like an ER form
    (with sections like "Notas de Enfermagem", "Medicação", etc.) that need cleanup.
    """
    print("[SEGMENTATION] Starting regex-based split of the OCR'd document...", flush=True)
    print(f"[SEGMENTATION] Document length: {len(full_text)} characters.", flush=True)

    indices = get_diary_start_indices(full_text)

    print(f"[SEGMENTATION] Regex found {len(indices)} diary start points.", flush=True)

    if not indices:
        print("[WARNING] Segmentation failed: no header pattern detected. Returning the whole block.", flush=True)
        return [{"title": "Documento Clínico Unificado", "text": full_text}]

    indices.append(len(full_text))
    diaries = []
    total_expected = len(indices) - 1

    for i in range(total_expected):
        start = indices[i]
        end = indices[i + 1]
        raw_segment = full_text[start:end].strip()

        if len(raw_segment) < 30:
            continue

        is_last = (i == total_expected - 1)

        clean_segment = re.sub(r'Diário\s+Clínico\s*\n*\s*Consulta\s+Externa', '', raw_segment, flags=re.IGNORECASE)
        clean_segment = clean_segment.replace("Diário Clínico", "").replace("Consulta Externa", "")
        clean_segment = re.sub(r'Pag\.\s*\d+\s*/\s*\d+', '', clean_segment, flags=re.IGNORECASE)
        clean_segment = re.sub(r'\n\s*\n+', '\n\n', clean_segment).strip()

        if is_last:
            urgency_pattern = r'\b(Notas de Enfermagem|Diagnósticos?|Medicação|Medicacao|MCDT Requisitados|Destino do Doente)\b'

            if re.search(urgency_pattern, clean_segment, re.IGNORECASE):
                print(f"[{i+1}/{total_expected}] ER-type document detected. Calling the LLM for final cleanup...", flush=True)
                
                system_prompt = """És um assistente médico especialista em curadoria de registos hospitalares.
Este é o último bloco do documento e pode conter secções administrativas e finais.
Se aparecerem:
1. DEVES REMOVER completamente as secções: "Notas de Enfermagem", "Medicação", "MCDT Requisitados" e "Destino do Doente".
2. DEVES MANTER a secção "Diagnósticos" (ou "Diagnosticos") e o seu respetivo conteúdo clínico.
3. Adiciona essa secção de Diagnósticos no final da narrativa clínica do médico.
4. Devolve exclusivamente o texto resultante limpo, sem comentários ou markdown."""
                    
                max_attempts = 3
                final_text = clean_segment  # fallback if all attempts fail

                for attempt in range(1, max_attempts + 1):
                    try:
                        raw_response = chat(client, user_prompt=clean_segment, system_prompt=system_prompt)
                        response = raw_response[0] if isinstance(raw_response, (tuple, list)) else str(raw_response)

                        if "504 Server Error" in response or "Gateway Timeout" in response:
                            raise ValueError("504 Timeout detected in the LLM response.")

                        final_text = response.strip()
                        break

                    except Exception as e:
                        print(f"[LLM URGENCY] Attempt {attempt}/{max_attempts} failed: {e}", flush=True)
                        if attempt < max_attempts:
                            time.sleep(5)
                        else:
                            print("[LLM URGENCY] Retry limit reached. Falling back to the original text.", flush=True)
            else:
                print(f"[{i+1}/{total_expected}] Consultation-type document detected. Skipping the LLM call.", flush=True)
                final_text = clean_segment
        else:
            final_text = clean_segment

        if len(final_text) > 10:
            title, visit_date = build_diary_title(raw_segment, i + 1)

            diaries.append({
                "id": i + 1,
                "title": title,
                "text": final_text,
                "visit_date": visit_date
            })
            print(f"Diary {i+1}/{total_expected} structured successfully: {title}", flush=True)

    return diaries