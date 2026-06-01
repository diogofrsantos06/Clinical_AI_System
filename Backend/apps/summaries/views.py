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