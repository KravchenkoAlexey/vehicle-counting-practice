# -*- coding: utf-8 -*-
"""Обработка видео: YOLOv8s + ByteTrack + подсчёт при пересечении линии."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

from config import CLASS_NAMES, COUNT_CLASS_IDS, IMG_SIZE


@dataclass
class CountStats:
    total: int = 0
    by_class: dict[str, int] = field(default_factory=dict)
    counted_tracks: set[int] = field(default_factory=set)
    frames_processed: int = 0
    fps_avg: float = 0.0
    duration_sec: float = 0.0
    snapshots: list[str] = field(default_factory=list)  # относительные имена файлов

    def add(self, class_id: int, track_id: int) -> None:
        if track_id in self.counted_tracks:
            return
        name = CLASS_NAMES[int(class_id)]
        self.by_class[name] = self.by_class.get(name, 0) + 1
        self.total += 1
        self.counted_tracks.add(track_id)


def _center_y(box: np.ndarray) -> float:
    return float((box[1] + box[3]) / 2)


def _crossed_line(prev_y: float | None, curr_y: float, line_y: float, downward: bool) -> bool:
    if prev_y is None:
        return False
    if downward:
        return prev_y < line_y <= curr_y
    return curr_y < line_y <= prev_y


def _save_crop(annotated: np.ndarray, box, path: Path, pad: int = 8) -> None:
    h, w = annotated.shape[:2]
    x1, y1, x2, y2 = map(int, box)
    x1, y1 = max(0, x1 - pad), max(0, y1 - pad)
    x2, y2 = min(w, x2 + pad), min(h, y2 + pad)
    if x2 <= x1 or y2 <= y1:
        return
    crop = annotated[y1:y2, x1:x2]
    cv2.imwrite(str(path), crop)


def process_video(
    video_path: Path,
    output_path: Path | None = None,
    model=None,
    line_y_ratio: float = 0.55,
    conf: float = 0.4,
    downward: bool = True,
    max_frames: int | None = None,
    progress_cb: Callable[[float, str], None] | None = None,
    snapshots_dir: Path | None = None,
    max_snapshots: int = 9,
) -> CountStats:
    """
    Обрабатывает видео: детекция, ByteTrack, подсчёт пересечений линии.
    Сохраняет скриншоты найденных машин в snapshots_dir.
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Не удалось открыть видео: {video_path}")

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_in = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    if max_frames:
        total_frames = min(total_frames, max_frames) if total_frames else max_frames

    line_y = int(h * line_y_ratio)
    writer = None
    if output_path is not None:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(output_path), fourcc, fps_in, (w, h))

    if snapshots_dir is not None:
        snapshots_dir.mkdir(parents=True, exist_ok=True)

    stats = CountStats()
    track_prev_y: dict[int, float] = {}
    snap_tracks: set[int] = set()
    t0 = time.perf_counter()
    frame_idx = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if max_frames and frame_idx >= max_frames:
            break

        results = model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            conf=conf,
            imgsz=IMG_SIZE,
            verbose=False,
        )
        r = results[0]
        annotated = frame.copy()

        # Линия подсчёта
        cv2.line(annotated, (0, line_y), (w, line_y), (0, 255, 255), 2)
        cv2.putText(
            annotated,
            "COUNT LINE",
            (10, max(20, line_y - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2,
        )

        if r.boxes is not None and len(r.boxes):
            boxes = r.boxes.xyxy.cpu().numpy()
            clss = r.boxes.cls.cpu().numpy().astype(int)
            confs = r.boxes.conf.cpu().numpy()
            ids = r.boxes.id
            track_ids = ids.cpu().numpy().astype(int) if ids is not None else None

            for i, (box, cls_id) in enumerate(zip(boxes, clss)):
                if int(cls_id) not in COUNT_CLASS_IDS:
                    continue
                x1, y1, x2, y2 = map(int, box)
                cy = _center_y(box)
                name = CLASS_NAMES[int(cls_id)]
                score = float(confs[i])
                tid = int(track_ids[i]) if track_ids is not None else -(i + 1)

                if _crossed_line(track_prev_y.get(tid), cy, line_y, downward):
                    stats.add(int(cls_id), tid)
                    if (
                        snapshots_dir is not None
                        and len(stats.snapshots) < max_snapshots
                        and tid not in snap_tracks
                    ):
                        fname = f"cross_{len(stats.snapshots)+1:02d}_{name}_id{tid}.jpg"
                        _save_crop(annotated, box, snapshots_dir / fname)
                        stats.snapshots.append(fname)
                        snap_tracks.add(tid)

                track_prev_y[tid] = cy
                color = (0, 255, 0)
                label = f"#{tid} {name} {score:.2f}"
                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                cv2.putText(annotated, label, (x1, max(15, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # Счётчик на кадре
        cv2.rectangle(annotated, (0, 0), (320, 70), (0, 0, 0), -1)
        cv2.putText(annotated, f"Count: {stats.total}", (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        for j, (cls_name, cnt) in enumerate(sorted(stats.by_class.items())):
            cv2.putText(
                annotated,
                f"{cls_name}: {cnt}",
                (10, 50 + j * 18),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (200, 200, 200),
                1,
            )

        # Дополнительные скрины: кадры с детекциями (каждые ~40 кадров)
        n_vehicles = 0
        if r.boxes is not None and len(r.boxes):
            clss_all = r.boxes.cls.cpu().numpy().astype(int)
            n_vehicles = sum(1 for c in clss_all if int(c) in COUNT_CLASS_IDS)

        if (
            snapshots_dir is not None
            and len(stats.snapshots) < max_snapshots
            and n_vehicles > 0
            and frame_idx % 40 == 0
        ):
            fname = f"frame_{len(stats.snapshots)+1:02d}_n{n_vehicles}.jpg"
            cv2.imwrite(str(snapshots_dir / fname), annotated)
            stats.snapshots.append(fname)

        if writer is not None:
            writer.write(annotated)
        frame_idx += 1
        stats.frames_processed = frame_idx

        if progress_cb and total_frames:
            progress_cb(frame_idx / total_frames, f"Кадр {frame_idx}/{total_frames}")

    cap.release()
    if writer is not None:
        writer.release()

    elapsed = time.perf_counter() - t0
    stats.duration_sec = round(elapsed, 2)
    stats.fps_avg = round(frame_idx / elapsed, 2) if elapsed > 0 else 0.0
    return stats
