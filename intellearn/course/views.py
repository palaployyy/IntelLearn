from django.views.generic import ListView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Q, Count
from .models import Course, Enrollment, Lesson
from .forms import CourseForm
from .forms import RegisterForm


# ✅ Home Page (ทุกคนเข้าได้ ไม่ต้อง login)
class HomeView(ListView):
    model = Course
    template_name = "home.html"
    context_object_name = "courses"

    def get_queryset(self):
        queryset = Course.objects.annotate(
            lesson_count=Count("lessons"),
            student_count=Count("enrollments")
        )
        search = self.request.GET.get("search")
        field = self.request.GET.get("field")

        if search:
            if field == "title":
                queryset = queryset.filter(title__icontains=search)
            elif field == "description":
                queryset = queryset.filter(description__icontains=search)
            elif field == "instructor":
                queryset = queryset.filter(instructor__username__icontains=search)
            else:
                queryset = queryset.filter(
                    Q(title__icontains=search) |
                    Q(description__icontains=search) |
                    Q(instructor__username__icontains=search)
                )
        return queryset


# ✅ Instructor: Add Course
def add_course(request):
    # เช็กว่าล็อกอินหรือยัง
    if not request.user.is_authenticated:
        return redirect("login")   # ถ้าไม่ล็อกอิน → ส่งไป login

    # เช็ก role (สมมติ instructor = staff)
    if not request.user.is_staff:
        return HttpResponseForbidden("Only instructors can add courses.")

    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            return redirect("home")
    else:
        form = CourseForm()

    return render(request, "course_form.html", {"form": form, "title": "Add New Course"})


def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if not request.user.is_authenticated:
        return redirect("login")

    if request.user != course.instructor and not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to edit this course.")

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = CourseForm(instance=course)

    return render(request, "course_form.html", {"form": form, "title": f"Edit Course: {course.title}"})



# ✅ Student: Course Detail (กดเข้าไปดู/Enroll ได้)
class CourseDetailView(DetailView):
    model = Course
    template_name = "course_detail.html"
    context_object_name = "course"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        user = self.request.user

        context["lessons"] = course.lessons.all()
        context["students_count"] = course.enrollments.count()
        context["is_enrolled"] = False

        if user.is_authenticated:
            context["is_enrolled"] = Enrollment.objects.filter(student=user, course=course).exists()

        return context

    def post(self, request, *args, **kwargs):
        """ ใช้ตอนกดปุ่ม Enroll """
        course = self.get_object()
        user = request.user

        if not user.is_authenticated:
            return redirect("login")

        # ถ้า enroll ไปแล้วไม่ต้องซ้ำ
        Enrollment.objects.get_or_create(student=user, course=course)
        return redirect("course_detail", pk=course.pk)


# ✅ Student: My Courses (แสดงคอร์สที่ลงทะเบียนไว้)
@login_required
def my_courses(request):
    courses = Course.objects.filter(enrollments__student=request.user)
    return render(request, "my_courses.html", {"courses": courses})

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login หลังสมัคร
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})
