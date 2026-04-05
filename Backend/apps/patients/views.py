from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Patient
from .serializers import PatientSerializer
from apps.summaries.services.patient_summary_service import generate_patient_summary

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    @action(detail=True, methods=["post"])
    def generate_summary(self, request, pk=None):
        """
        Generate or update the summary for this patient.
        Returns the summary text.
        """
        summary = generate_patient_summary(pk)

        return Response({
            "patient_id": pk,
            "summary_text": summary.summary_text
        })