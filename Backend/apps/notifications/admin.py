from django.contrib import admin
from .models import SystemNotification

@admin.register(SystemNotification)
class SystemNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'short_message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    readonly_fields = ('created_at',) # prevents accidentally editing the creation date

    def short_message(self, obj):
        if len(obj.message) > 50:
            return obj.message[:50] + '...'
        return obj.message

    short_message.short_description = 'Mensagem'
