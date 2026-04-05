from rest_framework import serializers
from .models import ClinicalDiary, ExtractedSections

class ExtractedSectionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedSections
        fields = ['sections_json', 'created_at']

class ClinicalDiarySerializer(serializers.ModelSerializer):
    sections = ExtractedSectionsSerializer(read_only=True)

    class Meta:
        model = ClinicalDiary
        fields = [
            'id', 
            'patient', 
            'diary_number', 
            'original_text', 
            'cleaned_text', 
            'sections', 
            'created_at'
        ]

class DiaryUploadSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField()
    file = serializers.FileField()