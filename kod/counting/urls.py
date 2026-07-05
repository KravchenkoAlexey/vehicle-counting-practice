from django.urls import path

from . import views

app_name = "counting"

urlpatterns = [
    path("", views.index, name="index"),
    path("process/", views.process_video_view, name="process"),
    path("result/<int:pk>/", views.result_view, name="result"),
    path("history/", views.history_view, name="history"),
    path("report/<int:pk>/", views.download_report, name="report"),
    path("history/export/", views.download_history_excel, name="history_export"),
]
