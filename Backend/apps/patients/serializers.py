from rest_framework import serializers

from apps.diaries.serializers import ClinicalDiarySerializer
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    summary = serializers.SerializerMethodField()
    diaries = ClinicalDiarySerializer(many=True, read_only=True)
    new_diaries_added = serializers.SerializerMethodField() 
    
    class Meta:
        model = Patient
        fields = ['id', 'nome', 'data_nascimento', 'numero_processo', 'sexo', 
            'telefone', 'email', 'n_sns', 'nif', 'subsistema', 
            'data_admissao', 'servico', 'medico', 'contacto_urg_nome', 
            'contacto_urg_telefone', 'summary', 'diaries', 'new_diaries_added','nacionalidade','morada']

        extra_kwargs = {
            'id': {'read_only': False}
        }

    def get_summary(self, obj):
        if hasattr(obj, 'clinical_summary'):
            summary = obj.clinical_summary
            return {
                "summary_text": summary.summary_text,
                "dados_estruturados": summary.dados_estruturados 
            }
        return None
    
    def get_new_diaries_added(self, obj):
        if not hasattr(obj, 'clinical_summary'):
            return True
        
        last_diary = obj.diaries.order_by('-created_at').first()
        if not last_diary:
            return False

        return last_diary.created_at > obj.clinical_summary.updated_at