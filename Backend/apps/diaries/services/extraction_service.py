import logging, time
from django.db import transaction
from ..models import ClinicalDiary
from apps.metrics.models import PerformanceMetric
from Pipeline.pipeline_extraction import ExtractionPipeline 
from apps.notifications.models import SystemNotification
from apps.summaries.models import Summary

logger = logging.getLogger(__name__)

def process_diary_batch(patient, lista_diarios_segmentados):
    """
    1. Guarda os textos brutos na BD imediatamente.
    2. Processa-os na LLM.
    3. Atualiza os registos na BD com a informação extraída.
    """
    try:
        # PASSO 1: GUARDAR IMEDIATAMENTE NA BD (Antes da IA atuar)
        diarios_db_map = {} # Dicionário para ligar o ID gerado ao título
        
        with transaction.atomic():
            for segmento in lista_diarios_segmentados:
                titulo = segmento.get("titulo", "Diário Desconhecido")
                
                # Cria o diário sem dados extraídos ainda
                diary_obj = ClinicalDiary.objects.create(
                    patient=patient,
                    title=titulo,
                    original_text=segmento.get("texto", ""),
                    cleaned_text="", 
                    extracted_data=None # Vazio para já
                )
                # Guarda o objeto para o podermos atualizar depois
                diarios_db_map[titulo] = diary_obj

        # PASSO 2: EXTRAÇÃO PELA LLM
        pipeline = ExtractionPipeline()
        logger.info(f"Iniciando extração em LOTE SEQUENCIAL para o paciente ID: {patient.id}")
        
        start_total = time.perf_counter()
        resultados_lote = pipeline.process_batch(lista_diarios_segmentados)
        total_duration = time.perf_counter() - start_total

        # PASSO 3: ATUALIZAR OS DIÁRIOS QUE JÁ ESTÃO NA BD
        for res in resultados_lote:
            titulo_diario = res.get("titulo")
            dados_extraidos = res.get("extracted_data")
            
            # Recupera o objeto exato que criámos no Passo 1
            diary = diarios_db_map.get(titulo_diario)
            
            if diary:
                if res.get("status") == "success":
                    
                    if not dados_extraidos:
                        SystemNotification.objects.create(
                            patient=patient,
                            message=f"O sistema não conseguiu extrair informação estruturada do documento '{titulo_diario}'. É necessária revisão manual."
                        )
                    
                    # Atualiza os dados
                    diary.cleaned_text = res.get("cleaned_text", "")
                    diary.extracted_data = dados_extraidos
                    diary.save() # Grava a atualização

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
                    logger.error(f"Falha na estruturação do diário '{titulo_diario}': {res.get('message')}")
                
        Summary.objects.get_or_create(
            patient=patient,
            defaults={"summary_text": "{}"} 
        )

        logger.info(f"Lote sequencial concluído com sucesso em {total_duration:.2f}s.")
        return True

    except Exception as e:
        logger.error(f"Erro crítico no lote do extraction_service: {e}")
        return False