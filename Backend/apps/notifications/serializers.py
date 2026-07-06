from rest_framework import serializers
from .models import SystemNotification

class SystemNotificationSerializer(serializers.ModelSerializer):
    # Formats the date on the backend so React doesn't have to
    data = serializers.SerializerMethodField()

    class Meta:
        model = SystemNotification
        fields = ['id', 'message', 'is_read', 'data']

    def get_data(self, obj):
        # e.g. "14/07/2023 às 15:30"
        return obj.created_at.strftime("%d/%m/%Y às %H:%M")