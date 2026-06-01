from rest_framework import serializers
from .models import Summary

class SummarySerializer(serializers.ModelSerializer):
    # Campo virtual calculado em tempo real
    dados_estruturados = serializers.SerializerMethodField()

    class Meta:
        model = Summary
        fields = ['id', 'patient', 'summary_text', 'updated_at', 'dados_estruturados']
