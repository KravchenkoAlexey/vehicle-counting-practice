# -*- coding: utf-8 -*-
from django import forms


class VideoProcessForm(forms.Form):
    video = forms.FileField(
        label="Видеофайл",
        help_text="MP4, AVI, MOV, MKV",
        widget=forms.ClearableFileInput(attrs={"accept": "video/*,.mp4,.avi,.mov,.mkv"}),
    )
    line_y_ratio = forms.FloatField(
        label="Линия подсчёта (доля высоты кадра)",
        min_value=0.1,
        max_value=0.9,
        initial=0.55,
        widget=forms.NumberInput(attrs={"step": "0.05"}),
    )
    conf = forms.FloatField(
        label="Порог уверенности (confidence)",
        min_value=0.1,
        max_value=0.9,
        initial=0.4,
        widget=forms.NumberInput(attrs={"step": "0.05"}),
    )
    downward = forms.BooleanField(
        label="Считать только движение сверху вниз",
        required=False,
        initial=True,
    )
    max_frames = forms.IntegerField(
        label="Макс. кадров (0 = всё видео)",
        min_value=0,
        initial=0,
        required=False,
    )
