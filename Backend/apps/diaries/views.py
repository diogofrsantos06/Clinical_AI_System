import tempfile, os, traceback, logging

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

from .services.extraction_service import process_diary_batch

from apps.patients.models import Patient
from apps.metrics.models import PerformanceMetric

logger = logging.getLogger(__name__)

class ClinicalDiaryViewSet(viewsets.ModelViewSet):
    queryset = ClinicalDiary.objects.all()
    serializer_class = ClinicalDiarySerializer

    @action(detail=False, methods=["post"], serializer_class=DiaryUploadSerializer)
    def upload_diary(self, request):
        upload_serializer = DiaryUploadSerializer(data=request.data)
        if not upload_serializer.is_valid():
            return Response(upload_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        patient_id = upload_serializer.validated_data["patient_id"]
        file = upload_serializer.validated_data["file"]

        client = None

        try:
            patient = Patient.objects.get(id=patient_id)

            client = get_client()

            ollama_warmup(client)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                for chunk in file.chunks():
                    tmp.write(chunk)
                temp_path = tmp.name

            clean_full_text, collected_metrics = extract_full_pdf_text(temp_path, client)

            if os.path.exists(temp_path):
                os.remove(temp_path)

            if collected_metrics:
                for metric in collected_metrics:
                    PerformanceMetric.objects.create(
                        operation_type=metric["operation_type"],
                        section_name=metric["section_name"],
                        duration_seconds=metric["duration_seconds"],
                        inference_duration=metric["inference_duration"],
                        tokens_per_second=metric.get("tokens_per_second", 0.0),
                        model_ram_gb=metric.get("model_ram_gb"),
                        model_vram_gb=metric.get("model_vram_gb"),
                        input_size=metric["input_size"],
                        is_retry=metric["is_retry"],
                        patient=patient
                    )
                print(f"[METRICS] Saved {len(collected_metrics)} OCR/cleanup metrics.", flush=True)

            if not clean_full_text.strip():
                return Response({"error": "O texto extraído do documento está vazio."}, status=status.HTTP_400_BAD_REQUEST)

            diary_list = run_smart_segmentation(clean_full_text, client)

            if not diary_list:
                return Response({"error": "Nenhum diário clínico foi segmentado com sucesso."}, status=status.HTTP_400_BAD_REQUEST)

            process_diary_batch(patient, diary_list)

            # A new upload invalidates the previous summary, so it gets regenerated below
            Summary.objects.filter(patient_id=patient_id).delete()
            print("Old summary deleted because new diaries came in.", flush=True)

            generate_patient_summary(patient_id)
            print(f"New summary automatically generated for patient {patient_id}.", flush=True)

            ollama_unload(client)

            return Response({
                "message": f"Sucesso! {len(diary_list)} diários detetados, estruturados e guardados.",
                "patient": patient.id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error("Diary upload pipeline failed", exc_info=True)
            return Response(
                {"error": "Ocorreu um erro interno ao processar o diário. Contacte o administrador se o problema persistir."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        finally:
            # Runs on every path (success and error alike): the explicit ollama_unload() above only
            # covers the success path, so this is what guarantees the model is freed if anything raised
            if client:
                try:
                    print("[FINALLY] Ensuring the model is released on the server...", flush=True)
                    ollama_unload(client)

                except Exception as unload_err:
                    print(f"Error while forcing unload in finally: {unload_err}", flush=True)
