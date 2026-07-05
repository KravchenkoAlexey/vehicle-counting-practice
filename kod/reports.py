# -*- coding: utf-8 -*-
"""Генерация отчётов Excel по истории обработки."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from config import COMPARISON_XLSX, METRICS_JSON, OUTPUT_DIR
from storage import load_history


def load_metrics_table() -> pd.DataFrame:
    if COMPARISON_XLSX.exists():
        return pd.read_excel(COMPARISON_XLSX)
    if METRICS_JSON.exists():
        import json

        data = json.loads(Path(METRICS_JSON).read_text(encoding="utf-8"))
        return pd.DataFrame(data)
    return pd.DataFrame()


def export_session_report(record: dict[str, Any], out_path: Path | None = None) -> Path:
    """Excel-отчёт по одной сессии обработки видео."""
    out_path = out_path or OUTPUT_DIR / f"report_session_{record.get('id', 'new')}.xlsx"

    summary = pd.DataFrame(
        [
            {"Параметр": "Видео", "Значение": record.get("video_name", "")},
            {"Параметр": "Дата", "Значение": record.get("timestamp", "")},
            {"Параметр": "Модель", "Значение": record.get("model", "YOLOv8s")},
            {"Параметр": "Всего пересечений", "Значение": record.get("total_count", 0)},
            {"Параметр": "Кадров обработано", "Значение": record.get("frames_processed", 0)},
            {"Параметр": "FPS обработки", "Значение": record.get("fps_avg", 0)},
            {"Параметр": "Время, сек", "Значение": record.get("duration_sec", 0)},
            {"Параметр": "Линия подсчёта (Y)", "Значение": record.get("line_y_ratio", "")},
            {"Параметр": "Confidence", "Значение": record.get("conf", "")},
        ]
    )
    by_class = pd.DataFrame(
        [{"Класс": k, "Количество": v} for k, v in (record.get("by_class") or {}).items()]
    )
    metrics = load_metrics_table()

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="Сводка", index=False)
        if not by_class.empty:
            by_class.to_excel(writer, sheet_name="По классам", index=False)
        if not metrics.empty:
            metrics.to_excel(writer, sheet_name="Сравнение моделей", index=False)

    return out_path


def export_full_history(out_path: Path | None = None) -> Path:
    out_path = out_path or OUTPUT_DIR / "history_all.xlsx"
    history = load_history()
    df = pd.DataFrame(history)
    metrics = load_metrics_table()
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="История", index=False)
        if not metrics.empty:
            metrics.to_excel(writer, sheet_name="Модели", index=False)
    return out_path
