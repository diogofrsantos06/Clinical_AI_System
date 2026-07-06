from rest_framework import serializers
from .models import Summary

class SummarySerializer(serializers.ModelSerializer):

    dados_estruturados = serializers.SerializerMethodField()

    class Meta:
        model = Summary
        fields = ['id', 'patient', 'summary_text', 'updated_at', 'dados_estruturados']

    def get_dados_estruturados(self, obj):
        return obj.dados_estruturados
