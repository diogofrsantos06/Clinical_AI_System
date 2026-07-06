import logging

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Summary
from .serializers import SummarySerializer
from .services.patient_summary_service import generate_patient_summary
from .triagem_service.triage_service import handle_triage_request

logger = logging.getLogger(__name__)


class SummaryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Summary.objects.all()
    serializer_class = SummarySerializer

    @action(detail=False, methods=["post"])
    def generate(self, request):    
        patient_id = request.data.get("patient_id")
        if not patient_id:
            return Response({"error": "patient_id is required"}, status=400)

        try:
            summary = Summary.objects.get(patient_id=patient_id)
            return Response(SummarySerializer(summary).data, status=status.HTTP_200_OK)
        except Summary.DoesNotExist:
            summary = generate_patient_summary(patient_id)
            if summary:
                return Response(SummarySerializer(summary).data, status=status.HTTP_200_OK)
            return Response({"error": "Failed to generate"}, status=400)
    
    @action(detail=False, methods=["post"])
    def analyze_triage(self, request):
        patient_id = request.data.get("patient_id")
        triage_text = request.data.get("triage_text")

        if not patient_id or not triage_text:
            return Response(
                {"error": "patient_id e triage_text são obrigatórios"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = handle_triage_request(patient_id, triage_text)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error("Triage analysis failed", exc_info=True)
            return Response(
                {"error": "Ocorreu um erro interno ao analisar a triagem. Contacte o administrador se o problema persistir."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )