from django.db import models

class Patient(models.Model):

    id = models.IntegerField(primary_key=True)

    def __str__(self):
        return f"Paciente {self.id}"