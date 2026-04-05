from django.contrib import admin
from .models import ClinicalDiary, ExtractedSections

admin.site.register(ClinicalDiary)
admin.site.register(ExtractedSections)
