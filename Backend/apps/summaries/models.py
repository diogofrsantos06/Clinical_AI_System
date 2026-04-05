from django.db import models

class Summary(models.Model):
    
    patient = models.OneToOneField("patients.Patient",on_delete=models.CASCADE,related_name="clinical_summary")

    summary_text = models.TextField()
    updated_at = models.DateTimeField(auto_now=True) 
    
    def __str__(self):
        return f"Summary for Patient {self.patient.id}"
