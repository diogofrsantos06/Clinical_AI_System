import json
from django.contrib import admin
from django.utils.html import format_html
from .models import Summary
from .serializers import SummarySerializer

@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'updated_at')
    readonly_fields = ('dados_estruturados_view',) # Criamos um nome diferente para o campo de leitura

    def dados_estruturados_view(self, obj):
        serializer = SummarySerializer(obj)
        data = serializer.data.get('dados_estruturados')
        
        if not data:
            return "Dados não disponíveis."
            
        json_pretty = json.dumps(data, indent=4, ensure_ascii=False)
        return format_html('<pre style="background:#f4f4f4; padding:10px;">{}</pre>', json_pretty)

    dados_estruturados_view.short_description = "Dados Estruturados (JSON Legível)"