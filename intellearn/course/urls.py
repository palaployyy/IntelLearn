from django.urls import path
from .views import (
    HomeView, add_course, edit_course,
    CourseDetailView, my_courses, register,
    add_lesson, edit_lesson, delete_lesson
)
from payment import views 

app_name = 'course'

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("add/", add_course, name="add_course"),
    path("<int:pk>/edit/", edit_course, name="edit_course"),  # ✅ ลบ "course/" ออก
    path("<int:pk>/", CourseDetailView.as_view(), name="course_detail"),  # ✅ ถูกต้อง
    path("my-courses/", my_courses, name="my_courses"),
    path("register/", register, name="register"),
    path("<int:course_id>/lesson/add/", add_lesson, name="add_lesson"),  # ✅ ลบ "course/" ออก
    path("lesson/<int:lesson_id>/edit/", edit_lesson, name="edit_lesson"),
    path("lesson/<int:lesson_id>/delete/", delete_lesson, name="delete_lesson"),
    path("list/", HomeView.as_view(), name="course_list"),
    path("<int:course_id>/payment/", views.payment_checkout.as_view(), name="checkout"),  # เพิ่ม URL สำหรับหน้า Payment
]
