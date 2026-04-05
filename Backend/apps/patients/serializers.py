from rest_framework import serializers

from apps.diaries.serializers import ClinicalDiarySerializer
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    summary = serializers.SerializerMethodField()
    diaries = ClinicalDiarySerializer(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'summary','diaries']

        extra_kwargs = {
            'id': {'read_only': False}
        }

    def get_summary(self, obj):
        if hasattr(obj, 'clinical_summary'):
            return obj.clinical_summary.summary_text
        return None