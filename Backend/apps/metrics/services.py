from django.db.models import Avg, Min, Max, Count
from .models import PerformanceMetric


def get_resource_usage_summary():
    """
    Summarizes model memory footprint and generation speed per operation type.

    Each PerformanceMetric row holds a point-in-time snapshot (taken right after
    that specific LLM call finished), not a running average during the call.
    Since the model stays loaded (keep_alive=-1), model_ram_gb/model_vram_gb
    should come out close to constant across rows of the same operation_type —
    a small (avg, min, max) spread here is itself evidence that the footprint is
    stable and predictable on the shared server, which is worth stating as such.
    """
    summary = (
        PerformanceMetric.objects
        .exclude(model_vram_gb__isnull=True)
        .values('operation_type')
        .annotate(
            amostras=Count('id'),
            vram_media_gb=Avg('model_vram_gb'),
            vram_min_gb=Min('model_vram_gb'),
            vram_max_gb=Max('model_vram_gb'),
            ram_media_gb=Avg('model_ram_gb'),
            tokens_por_segundo_media=Avg('tokens_per_second'),
        )
        .order_by('operation_type')
    )
    return list(summary)
