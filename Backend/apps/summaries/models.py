from django.db import models
import json
    
class Summary(models.Model):
    patient = models.OneToOneField("patients.Patient", on_delete=models.CASCADE, related_name="clinical_summary")
    summary_text = models.TextField()
    updated_at = models.DateTimeField(auto_now=True) 

    @property
    def dados_estruturados(self):
        try:
            return json.loads(self.summary_text)
        except (json.JSONDecodeError, TypeError):
            return {"resumo_texto": self.summary_text}
    
    def __str__(self):
        return f"Summary for Patient {self.patient.id}"
