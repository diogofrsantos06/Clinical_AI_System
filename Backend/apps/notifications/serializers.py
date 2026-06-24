from rest_framework import serializers
from .models import SystemNotification

class SystemNotificationSerializer(serializers.ModelSerializer):
    # Vamos formatar a data diretamente no backend para o React não ter trabalho
    data = serializers.SerializerMethodField()

    class Meta:
        model = SystemNotification
        fields = ['id', 'message', 'is_read', 'data']

    def get_data(self, obj):
        # Transforma num formato amigável, ex: "14/07/2023 às 15:30"
        return obj.created_at.strftime("%d/%m/%Y às %H:%M")