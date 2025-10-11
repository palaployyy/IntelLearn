from django.urls import path
from . import views

app_name = "course"

urlpatterns = [
    # หน้าโฮม/ลิสต์คอร์ส
    path("", views.HomeView.as_view(), name="home"),
    path("list/", views.HomeView.as_view(), name="course_list"),

    # จัดการคอร์ส
    path("add/", views.add_course, name="add_course"),
    path("<int:pk>/edit/", views.edit_course, name="edit_course"),
    path("delete/<int:course_id>/", views.delete_course_view, name="delete_course"),

    # รายละเอียดคอร์ส + enroll (POST ใน CourseDetailView)
    path("<int:pk>/", views.CourseDetailView.as_view(), name="course_detail"),

    # บทเรียน
    path("<int:course_id>/lesson/add/", views.add_lesson, name="add_lesson"),
    path("lesson/<int:lesson_id>/edit/", views.edit_lesson, name="edit_lesson"),
    path("lesson/<int:lesson_id>/delete/", views.delete_lesson, name="delete_lesson"),

    # นักเรียน/ผู้สอน
    path("my-courses/", views.my_courses, name="my_courses"),
    path("instructor/dashboard/", views.instructor_dashboard_view, name="instructor_dashboard"),

    # สมัครสมาชิก
    path("register/", views.register, name="register"),
]
