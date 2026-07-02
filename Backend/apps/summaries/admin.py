import json
from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html

from .models import Summary
from .serializers import SummarySerializer
from apps.summaries.services.patient_summary_service import generate_patient_summary

@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'updated_at')
    readonly_fields = ('dados_estruturados_view',) 

    actions = ['regenerar_sumario']

    def dados_estruturados_view(self, obj):
        serializer = SummarySerializer(obj)
        data = serializer.data.get('dados_estruturados')
        
        if not data:
            return "Dados não disponíveis."
            
        json_pretty = json.dumps(data, indent=4, ensure_ascii=False)
        return format_html('<pre style="background:#f4f4f4; padding:10px;">{}</pre>', json_pretty)

    dados_estruturados_view.short_description = "Dados Estruturados (JSON Legível)"

    @admin.action(description='Gerar Sumário Clínico')
    def regenerar_sumario(self, request, queryset):
        ids_pacientes = queryset.values_list('patient_id', flat=True)
        
        sucessos = 0
        falhas = 0
        
        for pid in ids_pacientes:
            if generate_patient_summary(pid, client=None) is not None:
                sucessos += 1
            else:
                falhas += 1