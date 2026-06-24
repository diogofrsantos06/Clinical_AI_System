from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import SystemNotification
from .serializers import SystemNotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = SystemNotificationSerializer
    
    def get_queryset(self):
        """
        O React vai chamar /api/notifications/?patient_id=X
        Nós filtramos para devolver SÓ as mensagens do paciente correto.
        """
        patient_id = self.request.query_params.get('patient_id')
        if patient_id:
            return SystemNotification.objects.filter(patient_id=patient_id)
        return SystemNotification.objects.none()

    @action(detail=False, methods=['post'])
    def mark_as_read(self, request):
        """
        O React chama esta rota quando o médico clica no sino para abrir a janela,
        para que o número vermelho desapareça.
        """
        patient_id = request.data.get('patient_id')
        if patient_id:
            SystemNotification.objects.filter(patient_id=patient_id, is_read=False).update(is_read=True)
            return Response({"message": "Notificações marcadas como lidas."})
            
        return Response({"error": "ID do paciente não fornecido."}, status=status.HTTP_400_BAD_REQUEST)