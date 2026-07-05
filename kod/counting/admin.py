from django.contrib import admin
from .models import ProcessingSession


@admin.register(ProcessingSession)
class ProcessingSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "video_name", "total_count", "frames_processed", "fps_avg", "created_at")
    list_filter = ("model_name", "created_at")
    readonly_fields = ("created_at",)
