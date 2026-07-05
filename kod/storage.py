# -*- coding: utf-8 -*-
"""Сохранение истории обработки в JSON."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from config import HISTORY_JSON


def load_history() -> list[dict[str, Any]]:
    if not HISTORY_JSON.exists():
        return []
    return json.loads(HISTORY_JSON.read_text(encoding="utf-8"))


def save_history(records: list[dict[str, Any]]) -> None:
    HISTORY_JSON.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_JSON.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def append_record(record: dict[str, Any]) -> dict[str, Any]:
    records = load_history()
    record = {
        "id": len(records) + 1,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        **record,
    }
    records.append(record)
    save_history(records)
    return record
