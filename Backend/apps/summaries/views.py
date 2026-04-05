from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Summary
from .serializers import SummarySerializer
from .services.patient_summary_service import generate_patient_summary

class SummaryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Summary.objects.all()
    serializer_class = SummarySerializer

    @action(detail=False, methods=["post"])
    def generate(self, request):
        """
        Gera ou atualiza o resumo de um paciente.
        """
        patient_id = request.data.get("patient_id")
        
        if not patient_id:
            return Response({"error": "patient_id is required"}, status=400)

        summary = generate_patient_summary(patient_id)
        
        if summary:
            return Response(SummarySerializer(summary).data, status=status.HTTP_200_OK)
        
        return Response({"error": "Failed to generate summary"}, status=status.HTTP_400_BAD_REQUEST)