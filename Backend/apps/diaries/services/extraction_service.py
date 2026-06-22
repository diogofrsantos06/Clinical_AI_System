import logging, time

from django.db import transaction

from ..models import ClinicalDiary
from apps.metrics.models import PerformanceMetric
from Pipeline.pipeline_extraction import ExtractionPipeline 

logger = logging.getLogger(__name__)

def process_diary_batch(patient, lista_diarios_segmentados):
    """
    Recebe os diários da segmentação, processa-os sequencialmente e grava no Django.
    Substitui a antiga lógica paralela problemática.
    """
    try:
        pipeline = ExtractionPipeline()
        logger.info(f"Iniciando extração em LOTE SEQUENCIAL para o paciente ID: {patient.id}")

        start_total = time.perf_counter()
        
        resultados_lote = pipeline.process_batch(lista_diarios_segmentados)
        
        total_duration = time.perf_counter() - start_total

        # Gravação Segura na Base de Dados
        with transaction.atomic():
            for res in resultados_lote:
                if res.get("status") == "success":
                    
                    diary = ClinicalDiary.objects.create(
                        patient=patient,
                        title=res.get("titulo"),
                        original_text=res.get("texto_original"),
                        cleaned_text=res.get("cleaned_text"),
                        extracted_data=res.get("extracted_data") 
                    )

                    PerformanceMetric.objects.create(
                        operation_type='EXTRACTION',
                        duration_seconds=total_duration / len(resultados_lote), 
                        inference_duration=res.get("tempo_llm", 0.0), 
                        is_retry=res.get("houve_retry", False),   
                        input_size=len(res.get("texto_original", "")), 
                        patient=patient,
                        diary=diary
                    )
                else:
                    logger.error(f"Falha na estruturação do diário '{res.get('titulo')}': {res.get('message')}")

        logger.info(f"Lote sequencial concluído com sucesso em {total_duration:.2f}s.")
        return True

    except Exception as e:
        logger.error(f"Erro crítico no lote do extraction_service: {e}")
        return False