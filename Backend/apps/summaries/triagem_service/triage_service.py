import time
from Pipeline.pipeline_triagem import TriagePipeline
from Pipeline.ollama_local_client import get_client, ollama_warmup, ollama_unload

from apps.metrics.models import PerformanceMetric
from apps.patients.models import Patient
from apps.summaries.models import Summary

def handle_triage_request(patient_id, triage_text):
    """Runs AI-assisted triage for a patient."""
    patient = Patient.objects.get(id=patient_id)

    summary_obj = getattr(patient, 'clinical_summary', None)
    
    if not summary_obj or not summary_obj.summary_text or summary_obj.summary_text.strip() in ["", "{}"]:
        print(f"[TRIAGE] Patient {patient_id} has no processed history yet. Aborting AI triage.", flush=True)
        
        return {
            "analise_texto": "Não é possível realizar a inferência clínica assistida porque este paciente ainda não possui documentação e histórico processados no sistema.",
            "dados_estruturados": {"exames": []},
            "tempo_llm": 0.0,
            "houve_retry": False
        }
    
    history = summary_obj.summary_text
    print(f"[TRIAGE] History validated. Starting the triage pipeline.", flush=True)

    client = get_client()
    ollama_warmup(client)

    pipeline = TriagePipeline()
    
    start_total = time.perf_counter()
    
    try:
        result = pipeline.run(triage_text, history)
    finally:
        ollama_unload(client)
    
    duration_total = time.perf_counter() - start_total
    
    if "error" not in result:
        PerformanceMetric.objects.create(
            operation_type='TRIAGE_ANALYSIS',
            duration_seconds=duration_total,
            inference_duration=result.get("tempo_llm", 0.0),
            tokens_per_second=result.get("tokens_per_second", 0.0),
            model_ram_gb=result.get("model_ram_gb"),
            model_vram_gb=result.get("model_vram_gb"),
            input_size=len(history) + len(triage_text),
            is_retry=result.get("houve_retry", False), 
            patient=patient
        )
    
    return result