# -*- coding: utf-8 -*-
"""Конфигурация демонстрационного приложения (раздел 3)."""
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
PRACTICE_ROOT = CODE_DIR.parent
VEHICLE_COUNTING = PRACTICE_ROOT / "vehicle-counting"

# Лучшая модель по результатам раздела 2
MODEL_WEIGHTS = VEHICLE_COUNTING / "runs" / "detect" / "yolov8s" / "weights" / "best.pt"
METRICS_JSON = VEHICLE_COUNTING / "results" / "all_metrics.json"
COMPARISON_XLSX = VEHICLE_COUNTING / "results" / "comparison.xlsx"

DATA_DIR = CODE_DIR / "data"
OUTPUT_DIR = CODE_DIR / "outputs"
HISTORY_JSON = DATA_DIR / "history.json"
UPLOADS_DIR = DATA_DIR / "uploads"

CLASS_NAMES = ["bicycle", "bus", "car", "motorbike", "rickshaw", "truck", "van"]
# Основные классы для подсчёта автомобилей (п. 1.3 отчёта)
COUNT_CLASS_IDS = {1, 2, 5, 6}  # bus, car, truck, van
COUNT_CLASS_NAMES = {CLASS_NAMES[i] for i in COUNT_CLASS_IDS}

IMG_SIZE = 640
DEFAULT_CONF = 0.4
DEFAULT_LINE_Y = 0.55  # доля высоты кадра (0–1)

for d in (DATA_DIR, OUTPUT_DIR, UPLOADS_DIR):
    d.mkdir(parents=True, exist_ok=True)
