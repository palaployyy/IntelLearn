# courses/urls.py
from django.urls import path
from .views import HomeView, edit_course, add_course, CourseDetailView, register

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("add/", add_course, name="add_course"),
    path("course/<int:pk>/edit/", edit_course, name="edit_course"),
    path("course/<int:pk>/", CourseDetailView.as_view(), name="course_detail"),
    path("register/", register, name="register"),
]
