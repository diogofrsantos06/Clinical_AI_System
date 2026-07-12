import logging, time, json

from apps.patients.models import Patient
from apps.diaries.models import ClinicalDiary
from apps.metrics.models import PerformanceMetric
from apps.notifications.models import SystemNotification
from ..models import Summary

from Pipeline.ollama_local_client import get_client, ollama_warmup, ollama_unload
from Pipeline.pipeline_summary import SummaryPipeline

logger = logging.getLogger(__name__)

def generate_patient_summary(patient_id, client=None):
    local_client = client
    owns_client = False

    if local_client is None:
        local_client = get_client()
        ollama_warmup(local_client)
        owns_client = True

    try:
        patient = Patient.objects.get(id=patient_id)

        diaries = ClinicalDiary.objects.filter(patient=patient, extracted_data__isnull=False).order_by('diary_number')

        if not diaries.exists():
            logger.warning(f"No extracted data found for patient {patient_id}")
            return None

        all_extractions = []
        for diary in diaries:
            safe_title = diary.title if diary.title else f"Diário {diary.diary_number}"

            all_extractions.append({
                "title": safe_title,
                "data": diary.extracted_data,
                "visit_date": diary.visit_date
            })

        summary_pipeline = SummaryPipeline()
        start_total = time.perf_counter()

        logger.info(f"Starting summary generation for patient ID: {patient_id}")

        summary_text, section_timings, had_retry = summary_pipeline.run_summary(all_extractions)

        if not summary_text or "Error code:" in summary_text or "rate_limit" in summary_text:
            logger.error("AI summary generation failed: empty result.")
            return None

        if "Erro: Não foi possível" in summary_text:
            SystemNotification.objects.create(
                patient=patient,
                message="Necessária intervenção do administrador devido a erro na geração de partes do Sumário Clínico (Recuperação Parcial ativada)."
            )
            logger.warning(f"[NOTIFICATION] Summary alarm triggered for patient {patient.id}.")

        total_duration = time.perf_counter() - start_total

        input_size = len(json.dumps(all_extractions))

        total_llm_inference_time = 0.0

        if isinstance(section_timings, dict):
            for section_name, section_metrics in section_timings.items():
                total_llm_inference_time += section_metrics["inference"]

                PerformanceMetric.objects.create(
                    operation_type='SUMM_SECTION',
                    section_name=section_name,
                    duration_seconds=section_metrics["duration"],
                    inference_duration=section_metrics["inference"],
                    tokens_per_second=section_metrics.get("tokens_per_second", 0.0),
                    model_ram_gb=section_metrics.get("model_ram_gb"),
                    model_vram_gb=section_metrics.get("model_vram_gb"),
                    input_size=section_metrics.get("input_size", 0),
                    is_retry=False,
                    patient=patient
                )

        PerformanceMetric.objects.create(
            operation_type='SUMMARIZATION_TOTAL',
            section_name='TOTAL',
            duration_seconds=total_duration,
            inference_duration=total_llm_inference_time,
            input_size=input_size,
            is_retry=had_retry,
            patient=patient
        )

        summary, created = Summary.objects.update_or_create(
            patient=patient,
            defaults={"summary_text": summary_text}
        )
        return summary

    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return None

    finally:
        if owns_client and local_client:
            ollama_unload(local_client)
