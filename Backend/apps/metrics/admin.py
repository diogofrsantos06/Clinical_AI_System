import csv
from django.http import HttpResponse
from django.contrib import admin
from .models import PerformanceMetric


@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'operation_type', 'section_name', 'created_at',
        'duration_seconds', 'tokens_per_second', 'is_retry', 'fallback_used',
        'patient',
    )
    list_filter = ('operation_type', 'is_retry', 'fallback_used', 'error_type', 'created_at')
    search_fields = ('patient__id',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    actions = ['export_as_csv']

    CSV_COLUNAS = [
        # Identificação
        'id', 'operation_type', 'section_name', 'created_at', 'patient_id', 'diary_id',
        # Desempenho
        'duration_seconds', 'inference_duration', 'input_size',
        'prompt_tokens', 'completion_tokens', 'tokens_per_second', 'finish_reason',
        # Estado do servidor no momento da chamada
        'model_ram_gb', 'model_vram_gb', 'kv_cache_usage_percent', 'requests_waiting',
        # Fiabilidade
        'is_retry', 'attempt_count', 'fallback_used', 'error_type',
    ]

    @admin.action(description='Exportar selecionados para CSV')
    def export_as_csv(self, request, queryset):
        
        campos_existentes = {f.name for f in self.model._meta.get_fields()}
        colunas = [c for c in self.CSV_COLUNAS if c.replace('_id', '') in campos_existentes or c in campos_existentes]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=performance_metrics.csv'

        writer = csv.writer(response)
        writer.writerow(colunas)

        for obj in queryset.order_by('created_at'):
            linha = []
            for campo in colunas:
                valor = getattr(obj, campo, '')
                linha.append(valor if valor is not None else '')
            writer.writerow(linha)

        return response