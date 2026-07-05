# -*- coding: utf-8 -*-
from django.db import models


class ProcessingSession(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    video_name = models.CharField(max_length=255, verbose_name="Имя файла")
    input_video = models.FileField(upload_to="uploads/", blank=True, null=True)
    output_video = models.FileField(upload_to="outputs/", blank=True, null=True)
    model_name = models.CharField(max_length=64, default="YOLOv8s")
    line_y_ratio = models.FloatField(default=0.55)
    conf = models.FloatField(default=0.4)
    downward = models.BooleanField(default=True)
    total_count = models.PositiveIntegerField(default=0)
    by_class = models.JSONField(default=dict, blank=True)
    frames_processed = models.PositiveIntegerField(default=0)
    fps_avg = models.FloatField(default=0)
    duration_sec = models.FloatField(default=0)
    snapshots = models.JSONField(default=list, blank=True, verbose_name="Скриншоты")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Сессия обработки"
        verbose_name_plural = "Сессии обработки"

    def __str__(self):
        return f"#{self.pk} {self.video_name} — {self.total_count}"
