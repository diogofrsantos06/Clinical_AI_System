from django.db import models
from apps.patients.models import Patient
from apps.diaries.models import ClinicalDiary

class PerformanceMetric(models.Model):
    OPERATION_CHOICES = [
        ('EXTRACTION', 'Extração de Diário'),
        ('SUMMARIZATION', 'Geração de Sumário'),
    ]

    operation_type = models.CharField(max_length=20, choices=OPERATION_CHOICES)
    duration_seconds = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Agora usamos a classe diretamente, sem aspas!
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    diary = models.ForeignKey(ClinicalDiary, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.operation_type} - {self.duration_seconds:.2f}s"