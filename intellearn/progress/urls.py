# progress/urls.py
from django.urls import path
from . import views

app_name = "progress"

urlpatterns = [
    path("my/", views.my_progress, name="my_progress"),  # (มีหรือไม่มีก็ได้)
    path("lesson/<int:lesson_id>/done/", views.mark_done, name="mark_done"),
    path("lesson/<int:lesson_id>/undone/", views.unmark_done, name="unmark_done"),
]
