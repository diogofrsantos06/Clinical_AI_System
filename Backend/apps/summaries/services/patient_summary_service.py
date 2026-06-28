import logging
import time 
import json

from apps.patients.models import Patient
from apps.diaries.models import ClinicalDiary
from ..models import Summary

from Pipeline.pipeline_summary import SummaryPipeline
from apps.metrics.models import PerformanceMetric
from apps.notifications.models import SystemNotification  

logger = logging.getLogger(__name__)

def generate_patient_summary(patient_id):
    try:
        patient = Patient.objects.get(id=patient_id)
        
        diaries = ClinicalDiary.objects.filter(patient=patient, extracted_data__isnull=False).order_by('diary_number')

        if not diaries.exists():
            logger.warning(f"Nenhum dado extraído encontrado para o paciente {patient_id}")
            return None

        all_information = []
        for diary in diaries:
            titulo_safe = diary.title if diary.title else f"Diário {diary.diary_number}"
            
            all_information.append({
                "titulo": titulo_safe,
                "dados": diary.extracted_data 
            })

        summary_pipeline = SummaryPipeline()
        start_total = time.perf_counter()

        logger.info(f"Iniciando a geração de sumário para o paciente ID: {patient_id}")

        summary_text, tempos_seccoes, houve_retry = summary_pipeline.run_summary(all_information)

        if not summary_text or "Error code:" in summary_text or "rate_limit" in summary_text:
            logger.error(f"Falha na IA. O retorno foi um erro: {summary_text}")
            return None 
        
        if "Erro: Não foi possível" in summary_text:
            SystemNotification.objects.create(
                patient=patient,
                message="Necessária intervenção do administrador devido a erro na geração de partes do Sumário Clínico (Recuperação Parcial ativada)."
            )
            logger.warning(f"[NOTIFICAÇÃO] Alarme de Sumário disparado para o paciente {patient.id}.")
        
        duration_total = time.perf_counter() - start_total
        
        input_size = len(json.dumps(all_information))

        total_llm_inferencia = 0.0
        
        if isinstance(tempos_seccoes, dict):

            for nome_seccao, metricas_sec in tempos_seccoes.items():
                total_llm_inferencia += metricas_sec["inference"]
                
                PerformanceMetric.objects.create(
                    operation_type='SUMM_SECTION',
                    section_name=nome_seccao,
                    duration_seconds=metricas_sec["duration"],
                    inference_duration=metricas_sec["inference"],
                    input_size=0, # Dinâmico ou opcional
                    is_retry=False, 
                    patient=patient
                )
                
        PerformanceMetric.objects.create(
            operation_type='SUMMARIZATION_TOTAL',
            section_name='TOTAL',
            duration_seconds=duration_total,     
            inference_duration=total_llm_inferencia,         
            input_size=input_size,                
            is_retry=houve_retry,                
            patient=patient
        )

        summary, created = Summary.objects.update_or_create(
            patient=patient,
            defaults={"summary_text": summary_text}
        )
        return summary

    except Exception as e:
        logger.error(f"Erro ao gerar resumo: {e}")
        return None