import sys, time

from pathlib import Path
from typing import Dict, Any

from Pipeline.Extraction_Codes.extraction import DiaryExtractor

BASE_DIR = Path(__file__).resolve().parent.parent 
sys.path.append(str(BASE_DIR))

class ExtractionPipeline:
    def __init__(self):
        self.extraction_prompt = BASE_DIR / "Pipeline" / "System_Prompts" / "Extraction.txt"
        self.extractor = DiaryExtractor(self.extraction_prompt)

    def run(self, raw_diary_text: str) -> Dict[str, Any]:
        start_time = time.perf_counter()

        try:
            extraction_result = self.extractor.extract_full_diary(raw_diary_text)

            total_duration = time.perf_counter() - start_time

            return {
                "status": "success",
                "extracted_data": extraction_result.get("data", []),
                "llm_duration": extraction_result.get("llm_duration", 0.0),
                "had_retry": extraction_result.get("had_retry", False),
                "tokens_per_second": extraction_result.get("tokens_per_second", 0.0),
                "model_ram_gb": extraction_result.get("model_ram_gb"),
                "model_vram_gb": extraction_result.get("model_vram_gb"),
                "prompt_tokens": extraction_result.get("prompt_tokens"),
                "completion_tokens": extraction_result.get("completion_tokens"),
                "finish_reason": extraction_result.get("finish_reason"),
                "attempt_count": extraction_result.get("attempt_count"),
                "kv_cache_usage_percent": extraction_result.get("kv_cache_usage_percent"),
                "requests_waiting": extraction_result.get("requests_waiting"),
                "fallback_used": extraction_result.get("fallback_used", False),
                "error_type": extraction_result.get("error_type"),
                "total_duration": total_duration
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error while running the extraction pipeline: {str(e)}"
            }

    def process_batch(self, diary_list: list) -> list:
        """Runs extraction sequentially over a batch of diaries, reusing run() for consistency."""
        if not diary_list:
            return []

        print(f"\n[PIPELINE] Starting sequential processing of {len(diary_list)} diaries...", flush=True)
        results = []

        for i, item in enumerate(diary_list):
            title = item.get("title", f"Diary_{i}")
            raw_text = item.get("text", "")

            if not raw_text.strip():
                results.append({"index":i,"title": title, "status": "error", "message": "Empty text", "original_text": raw_text})
                continue

            print(f"[{i+1}/{len(diary_list)}] Extracting: '{title}'", flush=True)

            result = self.run(raw_text)

            result["index"] = i
            result["title"] = title
            result["original_text"] = raw_text
            results.append(result)

        print("[PIPELINE] Batch processing complete!\n", flush=True)
        return results
