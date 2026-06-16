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
from Pipeline.llm import get_client 

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

        try:
            patient = Patient.objects.get(id=patient_id)
            
            # Inicializa o cliente Groq para reutilização em ambas as fases
            client_groq = get_client()
            
            # 1. Escrita temporária do ficheiro multipart enviado pelo frontend
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                for chunk in file.chunks(): 
                    tmp.write(chunk)
                temp_path = tmp.name
            
            # 2. Executa a Fase 1: Extração + OCR + Purificação por página + Injeção de Tags
            full_text_limpo = extract_full_pdf_text(temp_path, client_groq)
            os.remove(temp_path)  # Descarte imediato e seguro do ficheiro temporário

            # 3. Executa a Fase 2: Divisão exata por tags e pós-processamento de regras de negócio
            lista_diarios = run_smart_segmentation(full_text_limpo, client_groq)

            # 4. Gravação atómica dos blocos gerados na base de dados
            for diario_obj in lista_diarios:
                ClinicalDiary.objects.create(
                    patient=patient, 
                    title=diario_obj.get("titulo"),       
                    original_text=diario_obj.get("texto") 
                )
            
            # Invalidação do cache de resumos e regeneração automática
            Summary.objects.filter(patient_id=patient_id).delete()
            print("Resumo antigo apagado porque entraram novos diários!", flush=True)

            generate_patient_summary(patient_id)
            print(f"Novo sumário gerado automaticamente para o paciente {patient_id}.", flush=True)

            return Response({
                "message": f"Sucesso! {len(lista_diarios)} diários detetados e guardados.",
                "patient": patient.id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            import traceback
            traceback.print_exc() 
            return Response({"error": f"Falha na Pipeline: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)