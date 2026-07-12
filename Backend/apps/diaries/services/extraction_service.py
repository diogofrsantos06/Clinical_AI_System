import logging, time
from django.db import transaction
from ..models import ClinicalDiary
from apps.metrics.models import PerformanceMetric
from Pipeline.pipeline_extraction import ExtractionPipeline 
from apps.notifications.models import SystemNotification
from apps.summaries.models import Summary
from Pipeline.ollama_local_client import get_client, ollama_warmup, ollama_unload

logger = logging.getLogger(__name__)

def extract_single_diary(diary, client=None):
    """
    Re-runs extraction for a single, already-saved diary (used by the admin action,
    e.g. when the original batch extraction failed for that one diary).
    Warms up/unloads Ollama only when no client was passed in, same pattern as
    generate_patient_summary in patient_summary_service.py.
    """
    local_client = client
    owns_client = False

    if local_client is None:
        local_client = get_client()
        ollama_warmup(local_client)
        owns_client = True

    try:
        pipeline = ExtractionPipeline()
        result = pipeline.run(diary.original_text or "")

        if result.get("status") != "success":
            logger.error(f"Failed to (re)extract diary '{diary.title}': {result.get('message')}")
            return False

        extracted_data = result.get("extracted_data")

        if not extracted_data:
            SystemNotification.objects.create(
                patient=diary.patient,
                message=f"The system could not extract structured information from document '{diary.title}'. Manual review needed."
            )

        # None (not {}) when extraction genuinely failed, same reasoning as process_diary_batch
        diary.extracted_data = extracted_data if extracted_data else None
        diary.save()

        PerformanceMetric.objects.create(
            operation_type='EXTRACTION',
            duration_seconds=result.get("total_duration", 0.0),
            inference_duration=result.get("llm_duration", 0.0),
            is_retry=result.get("had_retry", False),
            tokens_per_second=result.get("tokens_per_second", 0.0),
            model_ram_gb=result.get("model_ram_gb"),
            model_vram_gb=result.get("model_vram_gb"),
            input_size=len(diary.original_text or ""),
            patient=diary.patient,
            diary=diary
        )
        return True

    except Exception as e:
        logger.error(f"Critical error re-extracting diary {diary.id}: {e}")
        return False

    finally:
        if owns_client and local_client:
            ollama_unload(local_client)

def process_diary_batch(patient, segmented_diaries):
    """
    1. Saves the raw diary texts to the DB immediately.
    2. Runs them through the LLM extraction pipeline.
    3. Updates the DB records with the extracted data.
    """
    try:
        # Step 1: persist raw diaries right away, before the LLM runs
        diary_objects = []
        
        with transaction.atomic():
            for segment in segmented_diaries:
                title = segment.get("title", "Diário Desconhecido")

                diary_obj = ClinicalDiary.objects.create(
                    patient=patient,
                    title=title,
                    original_text=segment.get("text", ""),
                    visit_date=segment.get("visit_date"),
                    extracted_data=None
                )
                diary_objects.append(diary_obj)

         # Step 2: run LLM extraction over the whole batch
        pipeline = ExtractionPipeline()
        logger.info(f"Starting sequential batch extraction for patient ID: {patient.id}")

        start_total = time.perf_counter()
        batch_results = pipeline.process_batch(segmented_diaries)
        total_duration = time.perf_counter() - start_total

        # Step 3: update the DB records created in step 1 with the extracted data
        for result in batch_results:
            index = result.get("index")
            diary_title = result.get("title")
            extracted_data = result.get("extracted_data")

            diary = diary_objects[index] if index is not None and index < len(diary_objects) else None

            if diary:
                if result.get("status") == "success":

                    if not extracted_data:
                        SystemNotification.objects.create(
                            patient=patient,
                            message=f"The system could not extract structured information from document '{diary_title}'. Manual review needed."
                        )

                    diary.extracted_data = extracted_data if extracted_data else None
                    diary.save()

                    PerformanceMetric.objects.create(
                        operation_type='EXTRACTION',
                        duration_seconds=result.get("total_duration", 0.0),
                        inference_duration=result.get("llm_duration", 0.0),
                        is_retry=result.get("had_retry", False),
                        tokens_per_second=result.get("tokens_per_second", 0.0),
                        model_ram_gb=result.get("model_ram_gb"),
                        model_vram_gb=result.get("model_vram_gb"), 
                        input_size=len(result.get("original_text", "")),
                        patient=patient,
                        diary=diary
                    )
                else:
                    logger.error(f"Failed to structure diary '{diary_title}': {result.get('message')}")

        Summary.objects.get_or_create(
            patient=patient,
            defaults={"summary_text": "{}"}
        )

        logger.info(f"Sequential batch completed successfully in {total_duration:.2f}s.")
        return True

    except Exception as e:
        logger.error(f"Critical error in extraction_service batch: {e}")
        return False