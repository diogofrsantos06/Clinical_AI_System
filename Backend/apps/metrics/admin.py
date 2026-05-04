from django.contrib import admin

from .models import PerformanceMetric

@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ('operation_type', 'duration_seconds', 'patient', 'created_at')
    
    list_filter = ('operation_type', 'created_at')
    
    search_fields = ('patient__id',)