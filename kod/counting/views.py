# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

CODE_DIR = Path(__file__).resolve().parent.parent
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from config import COMPARISON_XLSX, COUNT_CLASS_NAMES, METRICS_JSON, MODEL_WEIGHTS  # noqa: E402
from reports import export_full_history, export_session_report, load_metrics_table  # noqa: E402

from .forms import VideoProcessForm
from .models import ProcessingSession
from .services import run_video_processing


def index(request):
    return render(
        request,
        "counting/index.html",
        {
            "model_exists": MODEL_WEIGHTS.exists(),
            "model_path": str(MODEL_WEIGHTS),
            "count_classes": sorted(COUNT_CLASS_NAMES),
        },
    )


def process_video_view(request):
    if request.method == "POST":
        form = VideoProcessForm(request.POST, request.FILES)
        if form.is_valid():
            if not MODEL_WEIGHTS.exists():
                form.add_error(None, "Веса YOLOv8s не найдены. Проверьте config.py")
            else:
                from django.conf import settings

                video_file = form.cleaned_data["video"]
                session = ProcessingSession(
                    video_name=video_file.name,
                    line_y_ratio=form.cleaned_data["line_y_ratio"],
                    conf=form.cleaned_data["conf"],
                    downward=form.cleaned_data["downward"],
                )
                session.input_video.save(video_file.name, video_file, save=True)

                snapshots_dir = settings.MEDIA_ROOT / "snapshots" / str(session.pk)
                snapshots_dir.mkdir(parents=True, exist_ok=True)

                mf = form.cleaned_data.get("max_frames") or 0
                max_frames = int(mf) if mf > 0 else None

                stats = run_video_processing(
                    Path(session.input_video.path),
                    session.line_y_ratio,
                    session.conf,
                    session.downward,
                    max_frames,
                    snapshots_dir=snapshots_dir,
                )

                session.total_count = stats.total
                session.by_class = stats.by_class
                session.frames_processed = stats.frames_processed
                session.fps_avg = stats.fps_avg
                session.duration_sec = stats.duration_sec
                session.snapshots = [f"snapshots/{session.pk}/{name}" for name in stats.snapshots]
                session.save()

                return redirect("counting:result", pk=session.pk)
    else:
        form = VideoProcessForm()

    return render(
        request,
        "counting/process.html",
        {"form": form, "model_exists": MODEL_WEIGHTS.exists()},
    )


def result_view(request, pk):
    session = get_object_or_404(ProcessingSession, pk=pk)
    snapshot_urls = [f"/media/{path}" for path in (session.snapshots or [])]
    return render(
        request,
        "counting/result.html",
        {"session": session, "snapshot_urls": snapshot_urls},
    )


def history_view(request):
    sessions = ProcessingSession.objects.all()[:50]
    return render(request, "counting/history.html", {"sessions": sessions})


def download_report(request, pk):
    session = get_object_or_404(ProcessingSession, pk=pk)
    record = {
        "id": session.pk,
        "timestamp": session.created_at.isoformat(),
        "video_name": session.video_name,
        "model": session.model_name,
        "total_count": session.total_count,
        "by_class": session.by_class,
        "frames_processed": session.frames_processed,
        "fps_avg": session.fps_avg,
        "duration_sec": session.duration_sec,
        "line_y_ratio": session.line_y_ratio,
        "conf": session.conf,
    }
    path = export_session_report(record)
    return FileResponse(path.open("rb"), as_attachment=True, filename=path.name)


def download_history_excel(request):
    records = list(
        ProcessingSession.objects.values(
            "id", "created_at", "video_name", "total_count", "frames_processed",
            "fps_avg", "duration_sec", "line_y_ratio", "conf", "by_class",
        )
    )
    # Временно пишем в reports через JSON-совместимый формат
    import json
    from config import OUTPUT_DIR

    tmp = OUTPUT_DIR / "_django_history_export.json"
    for r in records:
        r["timestamp"] = str(r.pop("created_at"))
    tmp.write_text(json.dumps(records, ensure_ascii=False, default=str), encoding="utf-8")

    import pandas as pd

    path = OUTPUT_DIR / "history_all.xlsx"
    metrics = load_metrics_table()
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        pd.DataFrame(records).to_excel(writer, sheet_name="История", index=False)
        if not metrics.empty:
            metrics.to_excel(writer, sheet_name="Модели", index=False)
    return FileResponse(path.open("rb"), as_attachment=True, filename=path.name)
