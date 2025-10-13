from django.urls import path
from . import views

app_name = "progress"

urlpatterns = [
    path("my/", views.my_progress, name="my_progress"),
    path("course/<int:course_id>/students/", views.course_progress, name="course_progress"),
    path("lesson/<int:lesson_id>/done/", views.mark_done, name="mark_done"),
    path("lesson/<int:lesson_id>/undone/", views.unmark_done, name="unmark_done"),
]
