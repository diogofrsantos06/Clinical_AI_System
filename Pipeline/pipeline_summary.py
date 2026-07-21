import sys
from pathlib import Path

from Pipeline.Summary_Codes.Summarization import Summarizer

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
SUMMARY_SYSTEM_PROMPT_PATH = BASE_DIR / "Pipeline" / "System_Prompts" / "Summary.txt"


class SummaryPipeline:
    def __init__(self, client=None):
        self.summarizer = Summarizer(system_prompt_path=SUMMARY_SYSTEM_PROMPT_PATH)

    def run_summary(self, extractions: list) -> tuple:
        """
        Input: list of extracted diaries (JSON) coming from the DB.
        Output: (summary_text, section_timings, had_retry) tuple for the Django service.
        """
        try:
            structured_payload = {}
            visit_dates = {}
            diary_ids = {}

            for i, item in enumerate(extractions, start=1):
                diary_label = f"{item['title']} (Registo {i})"
                structured_payload[diary_label] = item["data"]
                visit_dates[diary_label] = item.get("visit_date")
                diary_ids[diary_label] = item.get("id")

            # Runs the summarizer, which internally executes the 4 domain-specific LLM calls
            summary_text, section_timings, had_retry = self.summarizer.generate_summary(structured_payload, visit_dates, diary_ids)

            # Sanity check: generate_summary() always returns structured JSON (schema-validated per section, with fallback values), so only an empty result means real failure.
            if not summary_text:
                return None, 0.0, False

            return summary_text, section_timings, had_retry

        except Exception as e:
            print(f"[PIPELINE] Critical error during summary generation: {str(e)}")
            return None, 0.0, False
