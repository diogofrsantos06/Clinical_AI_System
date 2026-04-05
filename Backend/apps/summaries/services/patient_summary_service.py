import logging

from apps.patients.models import Patient
from apps.diaries.models import ClinicalDiary
from ..models import Summary

from Pipeline.pipeline_summary import SummaryPipeline

logger = logging.getLogger(__name__)

def generate_patient_summary(patient_id):
    try:
        patient = Patient.objects.get(id=patient_id)
        
        diaries = ClinicalDiary.objects.filter(patient=patient, extracted_data__isnull=False).order_by('diary_number')

        if not diaries.exists():
            logger.warning(f"Nenhum dado extraído encontrado para o paciente {patient_id}")
            return None

        all_information = [diary.extracted_data for diary in diaries]

        summary_pipeline = SummaryPipeline()
        summary_text = summary_pipeline.run_summary(all_information)

        summary, created = Summary.objects.update_or_create(patient=patient,defaults={"summary_text": summary_text})

        return summary

    except Exception as e:
        logger.error(f"Erro ao gerar resumo para paciente {patient_id}: {e}")
        return None