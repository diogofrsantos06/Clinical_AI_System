from django.contrib import admin
from .models import SystemNotification

@admin.register(SystemNotification)
class SystemNotificationAdmin(admin.ModelAdmin):
    # 1. As colunas que vão aparecer na tabela
    list_display = ('id', 'patient', 'mensagem_curta', 'is_read', 'created_at')
    
    # 2. Filtros laterais (muito úteis para veres só as não lidas)
    list_filter = ('is_read', 'created_at')
    
    # 3. Impede que alguém altere a data de criação por engano
    readonly_fields = ('created_at',)

    # 4. O truque para a mensagem não partir o layout da tabela
    def mensagem_curta(self, obj):
        if len(obj.message) > 50:
            return obj.message[:50] + '...'
        return obj.message
    
    # Dá o nome à coluna na tabela
    mensagem_curta.short_description = 'Mensagem'