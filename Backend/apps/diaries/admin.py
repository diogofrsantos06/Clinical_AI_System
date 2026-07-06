from django.contrib import admin, messages
from .models import ClinicalDiary
from .services.extraction_service import extract_single_diary

@admin.register(ClinicalDiary)
class ClinicalDiaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'title', 'visit_date', 'has_extracted_data', 'created_at')
    list_filter = ('created_at',)

    actions = ['extract_diary']

    def has_extracted_data(self, obj):
        return bool(obj.extracted_data)
    has_extracted_data.boolean = True
    has_extracted_data.short_description = 'Extraído'

    @admin.action(description='Extrair informação clínica (LLM)')
    def extract_diary(self, request, queryset):
        successes = 0
        failures = 0

        for diary in queryset:
            if extract_single_diary(diary, client=None):
                successes += 1
            else:
                failures += 1

        if successes:
            messages.success(request, f"{successes} diário(s) extraído(s) com sucesso.")
        if failures:
            messages.error(request, f"{failures} diário(s) falharam na extração.")
