import time
from Pipeline.pipeline_triagem import TriagePipeline

from apps.metrics.models import PerformanceMetric
from apps.patients.models import Patient
from apps.summaries.models import Summary

def handle_triage_request(patient_id, triage_text):
    patient = Patient.objects.get(id=patient_id)

    summary_obj = getattr(patient, 'clinical_summary', None)
    
    if not summary_obj or not summary_obj.summary_text or summary_obj.summary_text.strip() in ["", "{}"]:
        print(f"DEBUG: Paciente {patient_id} sem histórico. A abortar triagem via IA.", flush=True)
        
        return {
            "analise_texto": "Não é possível realizar a inferência clínica assistida porque este paciente ainda não possui documentação e histórico processados no sistema.",
            "dados_estruturados": {"exames": []},
            "tempo_llm": 0.0,
            "houve_retry": False
        }
    
    history = summary_obj.summary_text
    print(f"DEBUG: Histórico validado. A iniciar pipeline de Triagem...", flush=True)

    pipeline = TriagePipeline()
    
    start_total = time.perf_counter()
    
    result = pipeline.run(triage_text, history)
    
    duration_total = time.perf_counter() - start_total
    
    if "error" not in result:
        PerformanceMetric.objects.create(
            operation_type='TRIAGE_ANALYSIS',
            duration_seconds=duration_total,
            inference_duration=result.get("dados_estruturados", {}).get("tempo_llm", 0.0),
            input_size=len(history) + len(triage_text),
            is_retry=result.get("houve_retry", False), 
            patient=patient
        )
    
    return result