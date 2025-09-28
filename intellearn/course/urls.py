# courses/urls.py
from django.urls import path
from .views import HomeView, edit_course, add_course

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("add/", add_course, name="add_course"),
    path("course/<int:pk>/edit/", edit_course, name="edit_course"),
]