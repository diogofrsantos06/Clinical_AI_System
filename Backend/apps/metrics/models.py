from django.db import models
from apps.patients.models import Patient
from apps.diaries.models import ClinicalDiary

class PerformanceMetric(models.Model):
    OPERATION_CHOICES = [
        ('OCR_PAGE', 'OCR de Página PDF (Tesseract)'),
        ('PRE_CLEAN_CHUNK', 'Limpeza Prévia LLM (Bloco PDF)'),
        ('EXTRACTION', 'Extração de Diário'),
        ('SUMM_SECTION', 'Sumarização por Secção (LLM)'),
        ('SUMMARIZATION_TOTAL', 'Geração de Sumário Global'),
    ]

    operation_type = models.CharField(max_length=25, choices=OPERATION_CHOICES)
    
    # Se aplicável, a que secção do sumário pertence (Ex: 'ANTECEDENTES', 'MEDICACAO')
    section_name = models.CharField(max_length=50, null=True, blank=True) 

    # Tempos
    duration_seconds = models.FloatField(help_text="Tempo total da operação (inclui código Python + LLM)")
    inference_duration = models.FloatField(default=0.0, help_text="Tempo exclusivo de inferência da LLM")
    
    # Tamanho e Velocidade
    input_size = models.IntegerField(help_text="Número de caracteres processados (Input)")
    tokens_per_second = models.FloatField(null=True, blank=True, help_text="Velocidade de geração da LLM")
    
    # Controlo de Erros
    is_retry = models.BooleanField(default=False, help_text="Se a LLM falhou a 1ª tentativa e precisou de retry")
    fallback_used = models.BooleanField(default=False, help_text="Se falhou as 3x e aplicou dados parciais/erros")

    # Relações
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True, related_name='metrics')
    diary = models.ForeignKey(ClinicalDiary, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        sec = f" ({self.section_name})" if self.section_name else ""
        return f"{self.operation_type}{sec} - {self.duration_seconds:.2f}s"