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

    def dados_estruturados_view(self, obj):
        serializer = SummarySerializer(obj)
        data = serializer.data.get('dados_estruturados')
        
        if not data:
            return "Dados não disponíveis."
            
        json_pretty = json.dumps(data, indent=4, ensure_ascii=False)
        return format_html('<pre style="background:#f4f4f4; padding:10px;">{}</pre>', json_pretty)

    dados_estruturados_view.short_description = "Dados Estruturados (JSON Legível)"

    @admin.action(description='🧠 Forçar Regeração do Sumário Clínico via IA')
    def regenerar_sumario(self, request, queryset):
        sucessos = 0
        falhas = 0
        
        for summary in queryset:
            try:
                # Vamos buscar o ID do paciente associado a este sumário selecionado
                # e passamos ao serviço de sumarização
                resultado = generate_patient_summary(summary.patient.id)
                
                if resultado:
                    sucessos += 1
                else:
                    falhas += 1
            except Exception as e:
                falhas += 1
                
        # 3. Damos feedback visual ao administrador (Avisos verdes ou vermelhos no topo)
        if sucessos > 0:
            self.message_user(
                request, 
                f"Sumário regenerado com sucesso para {sucessos} paciente(s).", 
                messages.SUCCESS
            )
        if falhas > 0:
            self.message_user(
                request, 
                f"Falha ao regenerar sumário para {falhas} paciente(s). Verifica se a IA está a responder.", 
                messages.WARNING
            )