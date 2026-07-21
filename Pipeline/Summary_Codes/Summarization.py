import json, re, time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timedelta, date

from Pipeline.llm import chat, get_client
from Pipeline.Prompts.Summary_Prompt import PROMPT_ANTECEDENTES, PROMPT_MEDICACAO, PROMPT_EXAMES, PROMPT_PLANO
from Pipeline.Summary_Codes.json_to_text import change_data_format


class Summarizer:
    def __init__(self, system_prompt_path: Path, client=None):
        """Loads the client and the system prompt used for every summarization call."""
        self.client = client if client else get_client()

        try:
            with open(system_prompt_path, 'r', encoding='utf-8') as f:
                self.system_prompt = f.read().strip()
        except Exception as e:
            self.system_prompt = "És um médico sénior. Resume o histórico clínico com precisão."
            print(f"Warning: could not read the system prompt at {system_prompt_path}: {e}")

    def process_llm_section(self, user_prompt: str, section_name: str, schema: dict, fallbacks: dict) -> tuple:
        """
        Runs up to 3 attempts, validates the JSON against the expected schema, and if all attempts
        fail, tries to salvage whichever fields came back correct (partial rescue).
        """
        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            try:
                stats = {}
                raw_response, duration, had_retry = chat(self.client, user_prompt, self.system_prompt, stats_sink=stats)
                response = raw_response[0] if isinstance(raw_response, (tuple, list)) else str(raw_response)

                if "504 Server Error" in response or "Gateway Timeout" in response:
                    raise ValueError("504 Timeout detected.")

                match = re.search(r'\{.*\}', response, re.DOTALL)
                if not match:
                    raise ValueError(f"No JSON block found. Response received: {response[:50]}...")

                json_str = match.group(0)
                data = json.loads(json_str)

                if not isinstance(data, dict):
                    raise ValueError("The returned JSON is not a base dictionary.")

                for key, expected_type in schema.items():
                    if key not in data:
                        raise ValueError(f"Required key '{key}' is missing.")
                    if not isinstance(data[key], expected_type):
                        raise ValueError(f"Key '{key}' has the wrong type. Expected: {expected_type.__name__}.")

                extra_stats = {
                    "prompt_tokens": stats.get("prompt_tokens"),
                    "completion_tokens": stats.get("completion_tokens"),
                    "finish_reason": stats.get("finish_reason"),
                    "attempt_count": stats.get("attempt_count", attempt),
                    "kv_cache_usage_percent": stats.get("kv_cache_usage_percent"),
                    "requests_waiting": stats.get("requests_waiting"),
                    "fallback_used": False,
                    "error_type": None,
                }
                return data, duration, (had_retry or attempt > 1), stats.get("generation_tokens_per_second", 0.0), stats.get("model_ram_gb"), stats.get("model_vram_gb"), extra_stats

            except Exception as e:
                print(f"[{section_name}] Attempt {attempt}/{max_attempts} failed: {e}", flush=True)

                if attempt < max_attempts:
                    print(f"[{section_name}] Waiting 5 seconds to recover...", flush=True)
                    time.sleep(5)
                else:
                    print(f"[{section_name}] Retry limit reached! Applying partial data rescue...", flush=True)
                    salvaged_data = {}
                    partial_data = {}

                    # Try to parse whatever the LLM produced on the last attempt, even if malformed
                    if 'response' in locals():
                        salvage_match = re.search(r'\{.*\}', response, re.DOTALL)
                        if salvage_match:
                            try:
                                partial_data = json.loads(salvage_match.group(0))
                            except Exception:
                                pass  # totally unreadable JSON, partial_data stays empty

                    for key, expected_type in schema.items():
                        if isinstance(partial_data, dict) and key in partial_data and isinstance(partial_data[key], expected_type):
                            salvaged_data[key] = partial_data[key]
                            print(f"[{section_name}] -> Key '{key}' was valid and was rescued!")
                        else:
                            salvaged_data[key] = fallbacks[key]
                            print(f"[{section_name}] -> Key '{key}' corrupted. Replaced with a safe error message.")

                    extra_stats = {
                        "prompt_tokens": None, "completion_tokens": None, "finish_reason": None,
                        "attempt_count": attempt, "kv_cache_usage_percent": None, "requests_waiting": None,
                        "fallback_used": True, "error_type": "invalid_json",
                    }
                    return salvaged_data, 0.0, True, 0.0, None, None, extra_stats

    def generate_summary(self, all_extractions: Dict[str, Any], visit_dates: Dict[str, Any]) -> tuple:
        """Runs the 4 domain-specific LLM calls (antecedentes, medicação, exames, plano) and merges them."""
        if not all_extractions:
            return "Nenhum dado disponível para sumarização.", 0.0, False

        print("\nSTARTING SCHEMA-BASED SUMMARIZATION")
        merged_summary = {}
        section_timings = {}
        any_retry = False
        start_global = time.perf_counter()

        def get_date(title):
            return visit_dates.get(title) or date.min

        # 1. ANTECEDENTES (medical history / diagnoses)
        start_section = time.perf_counter()
        text_antecedentes = change_data_format(all_extractions, target_section="diagnosticos")
        if text_antecedentes:
            print(f"[ANTECEDENTES] Started. Input: {len(text_antecedentes)} chars.", flush=True)
            user_prompt = PROMPT_ANTECEDENTES.format(extracted_data=text_antecedentes)

            schema = {"antecedentes": list}
            fallback = {"antecedentes": [{"diagnostico": "Erro: Não foi possível gerar o sumário de antecedentes.", "tipo": "N/A", "temporalidade": "N/A", "desde": "N/A"}]}

            data, duration, had_retry, tokens_per_sec, model_ram, model_vram, extra_stats = self.process_llm_section(user_prompt, "ANTECEDENTES", schema, fallback)
            merged_summary.update(data)
            if had_retry:
                any_retry = True
            section_timings["ANTECEDENTES"] = {"duration": time.perf_counter() - start_section, "inference": duration, "input_size": len(text_antecedentes), "tokens_per_second": tokens_per_sec, "model_ram_gb": model_ram, "model_vram_gb": model_vram, **extra_stats}
        else:
            print("[ANTECEDENTES] Skipped: no data available.", flush=True)

        # 2. MEDICATION AND ALLERGIES
        start_section = time.perf_counter()
        cutoff_date = (datetime.now() - timedelta(days=365)).date()  

        medication_candidates = []
        for title, content in all_extractions.items():
            visit_date = get_date(title)
            if visit_date < cutoff_date:
                continue

            medications = [m for m in content.get("medicacao", []) if m.get("tipo") != "administrada"]
            if medications:
                medication_candidates.append({'date': visit_date, 'title': title, 'medications': medications})

        # One representative per specialty: its own most recent diary with medication data.
        latest_per_specialty = {}
        for entry in medication_candidates:
            specialty = entry['title'].split(' - ')[0].strip()
            if specialty not in latest_per_specialty or entry['date'] > latest_per_specialty[specialty]['date']:
                latest_per_specialty[specialty] = entry

        representatives = []
        for specialty, entry in latest_per_specialty.items():
            if "HUC-URG" in specialty:
                anchor_date = entry['date']
                cluster_titles = []
                cluster_medications = []

                for candidate in medication_candidates:
                    if "HUC-URG" not in candidate['title'].split(' - ')[0]:
                        continue
                    if anchor_date - timedelta(days=3) <= candidate['date'] <= anchor_date:
                        cluster_titles.append(candidate['title'])
                        cluster_medications.extend(candidate['medications'])

                merged_title = entry['title'] if len(cluster_titles) <= 1 else f"{entry['title']} [episódio de urgência, inclui também: {', '.join(t for t in cluster_titles if t != entry['title'])}]"
                representatives.append({'date': anchor_date, 'title': merged_title, 'medications': cluster_medications})
            else:
                representatives.append(entry)
        

        representatives.sort(key=lambda x: x['date'])
        medication_dataset = {rep['title']: {"medicacao": rep['medications']} for rep in representatives}

        text_medication = change_data_format(medication_dataset, target_section="medicacao")
        text_allergies = change_data_format(all_extractions, target_section="alergias")  # allergies are kept in full, no date filtering
        text_medication_allergies = f"{text_medication}\n\n{text_allergies}".strip()

        if text_medication_allergies:
            print(f"[MEDICAÇÃO/ALERGIAS] Started. Input: {len(text_medication_allergies)} chars.", flush=True)
            user_prompt = PROMPT_MEDICACAO.format(extracted_data=text_medication_allergies)

            schema = {"medicacao": list, "alergias": list}
            fallback = {
                "medicacao": [{"farmaco": "N/A", "dosagem": "N/A", "posologia": "N/A", "indicacao": "N/A", "diario_origem": "N/A"}],
                "alergias": [{"substancia": "N/A", "reacao": "N/A", "registo_origem": "N/A"}]
            }

            data, duration, had_retry, tokens_per_sec, model_ram, model_vram, extra_stats = self.process_llm_section(user_prompt, "MEDICAÇÃO/ALERGIAS", schema, fallback)
            merged_summary.update(data)
            if had_retry:
                any_retry = True
            section_timings["MEDICAÇÃO"] = {"duration": time.perf_counter() - start_section, "inference": duration, "input_size": len(text_medication_allergies), "tokens_per_second": tokens_per_sec, "model_ram_gb": model_ram, "model_vram_gb": model_vram, **extra_stats}
        else:
            print("[MEDICAÇÃO/ALERGIAS] Skipped: no data available.", flush=True)

        # 3. EXAMES (complementary exams from the last year)
        start_section = time.perf_counter()
        one_year_ago = (datetime.now() - timedelta(days=365)).date()

        exams_to_format = {}
        for title, data in all_extractions.items():
            visit_date = get_date(title)
            if visit_date >= one_year_ago:
                complementary_exams = [e for e in data.get("exames", []) if e.get("categoria") != "exame_objetivo"]

                if complementary_exams:
                    exams_to_format[title] = {"exames": complementary_exams}
                    print(f"[DEBUG EXAMES] {len(complementary_exams)} complementary exams in: {title}")

        if exams_to_format:
            print("[EXAMES] Started. Processing exams from the last year.", flush=True)
            text_exams = change_data_format(exams_to_format, target_section="exames")
            if not text_exams:
                print("[DEBUG EXAMES] change_data_format returned empty!")

            user_prompt = PROMPT_EXAMES.format(extracted_data=text_exams)

            schema = {"exames": list}
            fallback = {"exames": [{"nome": "Sem exames realizados no último ano", "data": "N/A", "tipo_exame": "N/A", "resultado": "N/A"}]}

            data, duration, had_retry, tokens_per_sec, model_ram, model_vram, extra_stats = self.process_llm_section(user_prompt, "EXAMES", schema, fallback)

            if data and isinstance(data.get("exames"), list) and len(data["exames"]) > 0:
                if data["exames"][0].get("nome") != "Sem exames realizados no último ano":
                    merged_summary.update({"exames": data["exames"]})

            if had_retry:
                any_retry = True
            section_timings["EXAMES"] = {"duration": time.perf_counter() - start_section, "inference": duration, "input_size": len(text_exams), "tokens_per_second": tokens_per_sec, "model_ram_gb": model_ram, "model_vram_gb": model_vram, **extra_stats}
        else:
            print("[EXAMES] Skipped: no exams in the last year.", flush=True)
            merged_summary.update({"exames": [{"nome": "N/A", "data": "N/A", "tipo_exame": "N/A", "resultado": "Sem exames registados no último ano."}]})
            section_timings["EXAMES"] = {"duration": time.perf_counter() - start_section, "inference": 0.0, "input_size": 0, "tokens_per_second": 0.0, "model_ram_gb": None, "model_vram_gb": None, "prompt_tokens": None, "completion_tokens": None, "finish_reason": None, "attempt_count": None, "kv_cache_usage_percent": None, "requests_waiting": None, "fallback_used": False, "error_type": None}


        # 4. THERAPEUTIC PLAN (most recent care plan per specialty, last year)
        start_section = time.perf_counter()
        one_year_ago = (datetime.now() - timedelta(days=365)).date()

        latest_plan_per_specialty = {}
        plans_to_format = {}

        for title, content in all_extractions.items():
            visit_date = get_date(title)
            if visit_date < one_year_ago:
                continue

            # Strict normalization: letters and digits only, lowercase, so the same specialty doesn't get split into multiple keys due to spacing/punctuation differences
            raw_specialty = title.split(" - ")[0].strip()
            specialty_key = re.sub(r'[^a-zA-Z0-9]', '', raw_specialty).lower()

            if specialty_key not in latest_plan_per_specialty or visit_date > latest_plan_per_specialty[specialty_key]['date']:
                latest_plan_per_specialty[specialty_key] = {'date': visit_date, 'title': title}

        for specialty_key, info in latest_plan_per_specialty.items():
            selected_title = info['title']
            plans_to_format[selected_title] = all_extractions[selected_title]

        text_plans = change_data_format(plans_to_format, target_section="plano")

        if text_plans.strip():
            user_prompt = PROMPT_PLANO.format(extracted_data=text_plans.strip())

            schema = {"plano": list}
            fallback = {"plano": [{"especialidade": "N/A", "data": "N/A", "conteudo": "Erro ao gerar plano."}]}

            data, duration, had_retry, tokens_per_sec, model_ram, model_vram, extra_stats = self.process_llm_section(user_prompt, "PLANO", schema, fallback)
            merged_summary.update(data)

            if had_retry:
                any_retry = True
            section_timings["PLANO"] = {"duration": time.perf_counter() - start_section, "inference": duration, "input_size": len(text_plans), "tokens_per_second": tokens_per_sec, "model_ram_gb": model_ram, "model_vram_gb": model_vram, **extra_stats}

        final_summary_text = json.dumps(merged_summary, ensure_ascii=False)
        total_llm_time = sum(section["inference"] for section in section_timings.values())

        print(f"\n[DEBUG METRIC] Total real summarization time: {time.perf_counter() - start_global:.2f}s")
        print(f"[DEBUG METRIC] Summed LLM time: {total_llm_time:.2f}s")

        return final_summary_text.strip(), section_timings, any_retry
