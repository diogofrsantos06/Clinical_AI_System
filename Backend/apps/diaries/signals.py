from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.diaries.models import ClinicalDiary
from apps.diaries.services.extraction_service import process_clinical_diary


@receiver(post_save, sender=ClinicalDiary)
def run_diary_pipeline(sender, instance, created, **kwargs):

    if created:
        process_clinical_diary(instance.id)