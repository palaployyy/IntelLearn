from django.urls import path
from .views import HomeView, add_course, edit_course, CourseDetailView, my_courses, register

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("add/", add_course, name="add_course"),
    path("course/<int:pk>/edit/", edit_course, name="edit_course"),
    path("course/<int:pk>/", CourseDetailView.as_view(), name="course_detail"),
    path("my-courses/", my_courses, name="my_courses"),
    path("register/", register, name="register"),

]
