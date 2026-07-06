import json
from django.contrib import admin, messages
from django.utils.html import format_html

from .models import Summary
from .serializers import SummarySerializer
from apps.summaries.services.patient_summary_service import generate_patient_summary

@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'updated_at')
    readonly_fields = ('structured_data_view',)

    actions = ['regenerate_summary']

    def structured_data_view(self, obj):
        serializer = SummarySerializer(obj)
        data = serializer.data.get('dados_estruturados')

        if not data:
            return "Dados não disponíveis."

        json_pretty = json.dumps(data, indent=4, ensure_ascii=False)
        return format_html('<pre style="background:#f4f4f4; padding:10px;">{}</pre>', json_pretty)

    structured_data_view.short_description = "Dados Estruturados (JSON Legível)"

    @admin.action(description='Gerar Sumário Clínico')
    def regenerate_summary(self, request, queryset):
        patient_ids = queryset.values_list('patient_id', flat=True)

        successes = 0
        failures = 0

        for pid in patient_ids:
            if generate_patient_summary(pid, client=None) is not None:
                successes += 1
            else:
                failures += 1

        if successes:
            messages.success(request, f"{successes} sumário(s) gerado(s) com sucesso.")
        if failures:
            messages.error(request, f"{failures} sumário(s) falharam ao gerar.")
