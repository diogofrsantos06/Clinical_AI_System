import tempfile
import os
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ClinicalDiary
from .serializers import ClinicalDiarySerializer, DiaryUploadSerializer
from .utils.pdf_splitter import extract_full_pdf_text
from ..summaries.models import Summary

from Pipeline.pipeline_segmentation import run_smart_segmentation
from Pipeline.llm import get_client 

from apps.patients.models import Patient

class ClinicalDiaryViewSet(viewsets.ModelViewSet):
    queryset = ClinicalDiary.objects.all()
    serializer_class = ClinicalDiarySerializer

    @action(detail=False, methods=["post"], serializer_class=DiaryUploadSerializer)
    def upload_diary(self, request):

        # 1. Delegar a receção dos dados
        patient_id = request.data.get("patient_id") or request.POST.get("patient_id")
        file = request.FILES.get("file")

        if not patient_id or not file:
            return Response({"error": "Dados incompletos"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            patient = Patient.objects.get(id=patient_id)
            
            # 2. Delegar a extração do PDF (gera a string full_text)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                for chunk in file.chunks(): 
                    tmp.write(chunk)
                temp_path = tmp.name
            
            full_text = extract_full_pdf_text(temp_path)
            os.remove(temp_path) # Limpeza imediata

            # 3. Executar a Pipeline de Segmentação
            client_groq = get_client()
            lista_diarios = run_smart_segmentation(full_text, client_groq)

            # 4. Gravação Final
            # Cada pedaço gera um diário novo para este paciente
            for diario_obj in lista_diarios:
                ClinicalDiary.objects.create(
                    patient=patient, 
                    title=diario_obj.get("titulo"),       
                    original_text=diario_obj.get("texto") 
                )
            
            Summary.objects.filter(patient_id=patient_id).delete()
            print("Resumo antigo apagado porque entraram novos diários!", flush=True)

            return Response({
                "message": f"Sucesso! {len(lista_diarios)} diários detetados e guardados.",
                "patient": patient.id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Captura o erro real para sabermos se foi na IA ou no PDF
            return Response({"error": f"Falha no Pipeline: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)