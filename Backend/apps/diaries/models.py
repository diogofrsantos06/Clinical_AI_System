from django.db import models

class ClinicalDiary(models.Model):

    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE, related_name="diaries")
    diary_number = models.IntegerField(null=True, blank=True)

    original_text = models.TextField(null=True, blank=True)
    
    cleaned_text = models.TextField(null=True, blank=True)

    extracted_data = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Garante que não existem dois "Diário 1" para o MESMO paciente
        unique_together = ['patient', 'diary_number']
        ordering = ['patient', 'diary_number']

    def save(self, *args, **kwargs):
        if not self.diary_number:
            last_diary = ClinicalDiary.objects.filter(patient=self.patient).order_by("-diary_number").first()
            if last_diary:
                self.diary_number = last_diary.diary_number + 1
            else:
                self.diary_number = 1
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Paciente {self.patient.id} - Diário {self.diary_number}"


class ExtractedSections(models.Model):
    """Guarda a divisão semântica feita pelo SectionParser"""
    diary = models.OneToOneField(ClinicalDiary, on_delete=models.CASCADE, related_name="sections")
    sections_json = models.JSONField() 
    created_at = models.DateTimeField(auto_now_add=True)    
    