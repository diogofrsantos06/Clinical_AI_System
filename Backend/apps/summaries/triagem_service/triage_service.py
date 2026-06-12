from Pipeline.pipeline_triagem import TriagePipeline

from apps.metrics.models import PerformanceMetric
from apps.patients.models import Patient
from apps.summaries.models import Summary

def handle_triage_request(patient_id, triage_text):
    patient = Patient.objects.get(id=patient_id)

    summary_obj = getattr(patient, 'clinical_summary', None)
    
    if summary_obj and summary_obj.summary_text:
        history = summary_obj.summary_text
    else:
        history = "Sem histórico clínico disponível."
    
    print(f"DEBUG: Histórico encontrado? {'Sim' if history else 'Não'}")

    pipeline = TriagePipeline()
    result = pipeline.run(triage_text, history)

    print(f"DEBUG: Resultado da pipeline: {result}")
    
    # Grava métricas
    #PerformanceMetric.objects.create(
    #    operation_type='TRIAGE_ANALYSIS',
    #    inference_duration=result["tempo_llm"],
    #    is_retry=result["houve_retry"],
    #    patient=patient
    #)
    
    return result 