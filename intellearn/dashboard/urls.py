from django.urls import path
from .views import instructor_dashboard, student_dashboard

urlpatterns = [
    path("instructor/", instructor_dashboard, name="instructor_dashboard"),
    path("student/", student_dashboard, name="student_dashboard"),
]
