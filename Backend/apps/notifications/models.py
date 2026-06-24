from django.db import models
from apps.patients.models import Patient

class SystemNotification(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField(help_text="Mensagem de erro ou aviso sobre a pipeline da IA.")
    is_read = models.BooleanField(default=False, help_text="Indica se o utilizador já leu a notificação.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # Mostra sempre as mais recentes primeiro
        verbose_name = 'Notificação do Sistema'
        verbose_name_plural = 'Notificações do Sistema'

    def __str__(self):
        estado = "Lida" if self.is_read else "Não Lida"
        return f"Notificação: Paciente {self.patient.id} - {estado}"