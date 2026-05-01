import logging
from django.db import transaction
from ..models import ClinicalDiary
from Pipeline.pipeline_extraction import ExtractionPipeline 

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

        result = pipeline.run(diary.original_text)

        if result.get("status") == "success":

            with transaction.atomic():
                diary.cleaned_text = result.get("cleaned_text")
                diary.extracted_data = result.get("extracted_data")
                diary.save()

            logger.info(
                f"Diário {diary.diary_number} (Paciente: {diary.patient.id}) processado com sucesso."
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