# -*- coding: utf-8 -*-
"""Сервисы: загрузка модели, обработка видео."""
from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

# Корень проекта (код/) в path для config, video_counter
CODE_DIR = Path(__file__).resolve().parent.parent
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from config import MODEL_WEIGHTS  # noqa: E402
from video_counter import process_video  # noqa: E402


@lru_cache(maxsize=1)
def get_yolo_model():
    if not MODEL_WEIGHTS.exists():
        raise FileNotFoundError(f"Веса не найдены: {MODEL_WEIGHTS}")
    from ultralytics import YOLO

    return YOLO(str(MODEL_WEIGHTS))


def run_video_processing(
    input_path: Path,
    line_y_ratio: float,
    conf: float,
    downward: bool,
    max_frames: int | None,
    snapshots_dir: Path | None = None,
):
    model = get_yolo_model()
    return process_video(
        input_path,
        output_path=None,
        model=model,
        line_y_ratio=line_y_ratio,
        conf=conf,
        downward=downward,
        max_frames=max_frames,
        snapshots_dir=snapshots_dir,
        max_snapshots=9,
    )
