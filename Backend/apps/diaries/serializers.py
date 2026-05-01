from rest_framework import serializers
from .models import ClinicalDiary


class ClinicalDiarySerializer(serializers.ModelSerializer):

    class Meta:
        model = ClinicalDiary
        fields = [
            'id', 
            'patient', 
            'diary_number', 
            'original_text', 
            'cleaned_text', 
            'extracted_data',
            'title',
            'created_at'
        ]

class DiaryUploadSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField()
    file = serializers.FileField()