import logging
from django.db import transaction
from ..models import ClinicalDiary
from apps.metrics.models import PerformanceMetric
from Pipeline.pipeline_extraction import ExtractionPipeline 
import time

logger = logging.getLogger(__name__)

def process_clinical_diary(diary_id):
    """
    Serviço central que orquestra a limpeza, segmentação e extração de um diário.
    Liga a Pipeline de IA à base de dados do Django.
    """
    try:
        diary = ClinicalDiary.objects.get(id=diary_id)
        
        pipeline = ExtractionPipeline()

        logger.info(f"Iniciando processamento da Pipeline para o Diário ID: {diary_id}")

        start_total = time.perf_counter()

        result = pipeline.run(diary.original_text)

        if result.get("status") == "success":

            total_duration = time.perf_counter() - start_total

            PerformanceMetric.objects.create(
                operation_type='EXTRACTION',
                duration_seconds=total_duration,      
                inference_duration=result["tempo_llm"], 
                is_retry=result["houve_retry"],   
                input_size=len(diary.original_text), 
                patient=diary.patient,
                diary=diary
            )

            with transaction.atomic():
                diary.cleaned_text = result.get("cleaned_text")
                diary.extracted_data = result.get("extracted_data")
                diary.save()

            logger.info(
                f"Diário {diary.diary_number} (Paciente: {diary.patient.id}) processado com sucesso em {total_duration:.2f}s."
                )
            
            return True
        
        else:
            logger.error(f"Erro retornado pela Pipeline: {result.get('message')}")
            return False

    except ClinicalDiary.DoesNotExist:
        logger.error(f"Erro: O Diário com ID {diary_id} não foi encontrado na base de dados.")
        return False
        
    except Exception as e:
        logger.error(f"Erro crítico no extraction_service: {str(e)}")
        print(f"Erro detalhado: {e}") 
        return False

def process_all_diaries_parallel(patient, lista_diarios_segmentados):
    """
    Pega nas consultas da segmentação, corre as extrações estruturadas
    todas ao mesmo tempo via Threads e grava-as de uma só vez no Django.
    """
    try:
        pipeline = ExtractionPipeline()
        logger.info(f"Iniciando extração em LOTE PARALELO para o paciente ID: {patient.id}")

        start_total = time.perf_counter()
        
        # Executa a extração concorrente através do método paralelo da pipeline
        resultados_lote = pipeline.run_parallel(lista_diarios_segmentados)
        
        total_duration = time.perf_counter() - start_total

        # Gravação em Bloco Segura na Base de Dados
        with transaction.atomic():
            for i, res in enumerate(resultados_lote):
                texto_original = lista_diarios_segmentados[i].get("texto")
                clean_text = pipeline.cleaner.clean_diary(texto_original)

                if res.get("status") == "success":
                    # CRIAMOS O REGISTO JÁ COM OS DADOS EXTRAÍDOS PREENCHIDOS!
                    diary = ClinicalDiary.objects.create(
                        patient=patient,
                        title=res.get("titulo"),
                        original_text=texto_original,
                        cleaned_text=clean_text,
                        extracted_data=res.get("dados")  # O JSON entra aqui direto
                    )

                    # Criar a métrica de performance individual correspondente
                    PerformanceMetric.objects.create(
                        operation_type='EXTRACTION',
                        duration_seconds=total_duration / len(resultados_lote), # Tempo médio por diário
                        inference_duration=res.get("tempo_llm", 0.0), 
                        is_retry=res.get("houve_retry", False),   
                        input_size=len(texto_original), 
                        patient=patient,
                        diary=diary
                    )
                else:
                    logger.error(f"Falha na estruturação do diário '{res.get('titulo')}': {res.get('message')}")

        logger.info(f"Processamento em lote concluído com sucesso total em {total_duration:.2f}s.")
        return True

    except Exception as e:
        logger.error(f"Erro crítico no lote paralelo do extraction_service: {e}")
        return False