import json

def change_data_format(extracted_json, target_section=None):
    """Flattens the per-diary extracted JSON into a plain-text block the LLM can read for one summary section."""
    if isinstance(extracted_json, str):
        try:
            extracted_json = json.loads(extracted_json)
        except Exception:
            return ""

    final_text = ""

    # Maps each JSON field to the section title shown in the formatted text
    section_titles = {
        "diagnosticos": "Diagnósticos",
        "medicacao": "Medicação Habitual",
        "alergias": "Alergias",
        "exames": "Exames e Resultados",
        "sintomas": "Sintomas",
        "plano": "Plano Terapêutico"
    }

    if target_section:
        sections_to_process = {target_section: section_titles.get(target_section, target_section)}
    else:
        sections_to_process = section_titles

    seen_diagnoses = set()
    empty_terms = {"sem informação", "n/a", "desconhecido", "não aplicável", "nenhum", "nenhuma"}

    # Loop over each diary 
    for diary_name, content in extracted_json.items():
        diary_block_text = ""

        for field, title in sections_to_process.items():
            field_items = content.get(field, [])

            if not field_items:
                continue

            section_lines = ""

            for item in field_items:
                details = []

                # PLANO (and other long free-text sections) may come as plain strings instead of dicts
                if isinstance(item, str):
                    section_lines += f"- {item}\n"
                    continue

                for key, value in item.items():
                    if value:
                        value_str = str(value).strip()

                        if field != "plano" and value_str.lower() in empty_terms:
                            continue

                        details.append(f"{key.replace('_', ' ').capitalize()}: {value_str}")

                if not details:
                    continue

                if field == "diagnosticos":
                    item_signature = " | ".join(details).lower()
                    if item_signature not in seen_diagnoses:
                        seen_diagnoses.add(item_signature)
                        section_lines += f"- {' | '.join(details)}\n"
                else:
                    section_lines += f"- {' | '.join(details)}\n"

            if section_lines:
                diary_block_text += f"{title}\n{section_lines}\n"

        if diary_block_text:
            final_text += f"--- IDENTIFICAÇÃO E DATA DO REGISTO: {diary_name} ---\n{diary_block_text}\n"

    return final_text.strip()


def summary_json_to_text(summary_json):
    """Flattens the already-merged patient summary (antecedentes/exames) into a plain-text
    block the LLM can read — same visual style as change_data_format, but for the flat
    summary structure instead of the per-diary extraction structure."""
    if isinstance(summary_json, str):
        try:
            summary_json = json.loads(summary_json)
        except Exception:
            return ""

    section_titles = {
        "antecedentes": "Diagnósticos",
        "exames": "Exames e Resultados",
    }

    final_text = ""

    for field, title in section_titles.items():
        field_items = summary_json.get(field, [])
        if not field_items:
            continue

        section_lines = ""
        for item in field_items:
            if isinstance(item, str):
                section_lines += f"- {item}\n"
                continue

            details = [f"{key.replace('_', ' ').capitalize()}: {str(value).strip()}"
                       for key, value in item.items() if value]

            if details:
                section_lines += f"- {' | '.join(details)}\n"

        if section_lines:
            final_text += f"{title}\n{section_lines}\n"

    return final_text.strip()