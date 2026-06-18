import tempfile
import os
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ClinicalDiary
from .serializers import ClinicalDiarySerializer, DiaryUploadSerializer
from .utils.pdf_splitter import extract_full_pdf_text
from ..summaries.models import Summary
from ..summaries.services.patient_summary_service import generate_patient_summary

from Pipeline.pipeline_segmentation import run_smart_segmentation
from Pipeline.llm import get_client, ollama_warmup, ollama_unload

from .services.extraction_service import process_all_diaries_parallel

from apps.patients.models import Patient

class ClinicalDiaryViewSet(viewsets.ModelViewSet):
    queryset = ClinicalDiary.objects.all()
    serializer_class = ClinicalDiarySerializer

    @action(detail=False, methods=["post"], serializer_class=DiaryUploadSerializer)
    def upload_diary(self, request):
        patient_id = request.data.get("patient_id") or request.POST.get("patient_id")
        file = request.FILES.get("file")

        if not patient_id or not file:
            return Response({"error": "Dados incompletos"}, status=status.HTTP_400_BAD_REQUEST)

        client_groq = None

        try:
            patient = Patient.objects.get(id=patient_id)
            
            # SUBSTITUIR O NOME
            client_groq = get_client()

            ollama_warmup(client_groq)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                for chunk in file.chunks(): 
                    tmp.write(chunk)
                temp_path = tmp.name
            
            full_text_limpo = extract_full_pdf_text(temp_path, client_groq)
            os.remove(temp_path) 

            lista_diarios = run_smart_segmentation(full_text_limpo, client_groq)

            process_all_diaries_parallel(patient, lista_diarios)
            
            Summary.objects.filter(patient_id=patient_id).delete()
            print("Resumo antigo apagado porque entraram novos diários!", flush=True)

            generate_patient_summary(patient_id)
            print(f"Novo sumário gerado automaticamente para o paciente {patient_id}.", flush=True)

            ollama_unload(client_groq)

            return Response({
                "message": f"Sucesso! {len(lista_diarios)} diários detetados, estruturados e guardados.",
                "patient": patient.id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            import traceback
            traceback.print_exc() 
            return Response({"error": f"Falha na Pipeline: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            if client_groq:
                try:
                    from Pipeline.llm import ollama_unload
                    print("[FINALLY] Garantindo a libertação do modelo no servidor...", flush=True)
                    ollama_unload(client_groq) 
                except Exception as unload_err:
                    print(f"Erro ao tentar forçar o unload no finally: {unload_err}", flush=True)