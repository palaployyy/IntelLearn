# course/views.py
from django.views.generic import ListView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import HttpResponseForbidden
from django.db.models import Q, Count
from django import forms
from django.contrib import messages

from .models import Course, Enrollment, Lesson
from .forms import CourseForm, RegisterForm
from payment.models import Payment
from progress.models import LearningProgress

# ✅ ป้องกัน error หาก progress app ยังไม่โหลด
try:
    from progress.models import LearningProgress
except Exception:
    LearningProgress = None


# ===========================
# Home
# ===========================
class HomeView(ListView):
    model = Course
    template_name = "home.html"
    context_object_name = "courses"

    def get_queryset(self):
        qs = Course.objects.annotate(
            lesson_count=Count("lessons"),
            student_count=Count("enrollments"),
        )
        search = self.request.GET.get("search")
        field = self.request.GET.get("field")
        if search:
            if field == "title":
                qs = qs.filter(title__icontains=search)
            elif field == "description":
                qs = qs.filter(description__icontains=search)
            elif field == "instructor":
                qs = qs.filter(instructor__username__icontains=search)
            else:
                qs = qs.filter(
                    Q(title__icontains=search)
                    | Q(description__icontains=search)
                    | Q(instructor__username__icontains=search)
                )
        return qs


# ===========================
# Add / Edit Course (สำหรับเดโม เปิดกว้าง)
# ===========================
def add_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user if request.user.is_authenticated else None
            course.save()
            messages.success(request, "สร้างคอร์สเรียบร้อย")
            return redirect("course:home")
    else:
        form = CourseForm()
    return render(request, "course_form.html", {"form": form, "title": "Add New Course"})


def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "แก้ไขคอร์สเรียบร้อย")
            return redirect("course:home")
    else:
        form = CourseForm(instance=course)
    return render(
        request, "course_form.html", {"form": form, "title": f"Edit Course: {course.title}"}
    )


# ===========================
# Course Detail + Enroll
# ===========================
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

        # ค่าดีฟอลต์
        context["pct"] = 0
        context["completed_ids"] = set()

        if user.is_authenticated:
            # หา enrollment ของผู้ใช้ในคอร์สนี้
            enrollment = Enrollment.objects.filter(student=user, course=course).first()
            context["enrollment"] = enrollment

            if enrollment:
                # ดึง/สร้าง progress
                progress, _ = LearningProgress.objects.get_or_create(enrollment=enrollment)
                context["pct"] = progress.percentage
                context["completed_ids"] = set(
                    progress.completed_lessons.values_list("id", flat=True)
                )

        return context

# ===========================
# My Courses / Register
# ===========================
@login_required
def my_courses(request):
    """
    แสดงคอร์สที่ user ลงทะเบียน และ % ความคืบหน้าของแต่ละคอร์ส
    """
    enrollments = (
        Enrollment.objects
        .select_related("course")
        .filter(student=request.user)
        .order_by("-id")
    )

    rows = []
    for en in enrollments:
        prog, _ = LearningProgress.objects.get_or_create(enrollment=en)
        total = en.course.lessons.count()
        done = prog.completed_lessons.count()
        rows.append({
            "course": en.course,
            "pct": prog.percentage,
            "done": done,
            "total": total,
        })

    return render(request, "my_courses.html", {"rows": rows})


# ===========================
# Lesson CRUD
# ===========================
class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["title", "content", "video_url", "order"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Lesson title"}
            ),
            "content": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "Lesson content"}
            ),
            "video_url": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "Video URL"}
            ),
            "order": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Order"}
            ),
        }


def add_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, "เพิ่มบทเรียนแล้ว")
            return redirect("course:course_detail", pk=course.id)
    else:
        form = LessonForm()
    return render(
        request, "lesson_form.html", {"form": form, "title": f"Add Lesson to {course.title}"}
    )


def edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == "POST":
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, "แก้ไขบทเรียนแล้ว")
            return redirect("course:course_detail", pk=lesson.course.id)
    else:
        form = LessonForm(instance=lesson)
    return render(
        request, "lesson_form.html", {"form": form, "title": f"Edit Lesson: {lesson.title}"}
    )


def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course_id = lesson.course.id
    lesson.delete()
    messages.success(request, "ลบบทเรียนแล้ว")
    return redirect("course:course_detail", pk=course_id)


# ===========================
# Delete Course (ต้องเป็น instructor)
# ===========================
@login_required
def delete_course_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if course.instructor != request.user and not request.user.is_superuser:
        messages.error(request, "คุณไม่มีสิทธิ์ลบคอร์สนี้")
        return redirect("course:home")

    if request.method == "POST":
        course.delete()
        messages.success(request, "ลบคอร์สเรียบร้อยแล้ว")
        return redirect("course:home")

    return render(request, "confirm_delete.html", {"course": course})


# ===========================
# Instructor Dashboard (อย่างง่าย)
# ===========================
@login_required
def instructor_dashboard_view(request):
    # ตัวอย่าง: ใช้กลุ่มชื่อ instructor
    if not request.user.groups.filter(name="instructor").exists() and not request.user.is_superuser:
        return redirect("course:home")

    courses = Course.objects.filter(instructor=request.user)

    course_data = []
    for c in courses:
        enrollments = Enrollment.objects.filter(course=c)
        total_students = enrollments.count()
        completed = enrollments.filter(status="completed").count()
        active = enrollments.filter(status="active").count()
        dropped = enrollments.filter(status="dropped").count()

        course_data.append(
            {
                "course": c,
                "total_students": total_students,
                "completed": completed,
                "active": active,
                "dropped": dropped,
            }
        )

    context = {
        "course_data": course_data,
        "total_courses": courses.count(),
        "total_students": Enrollment.objects.filter(course__in=courses).count(),
        "total_revenue": sum([c.price * Enrollment.objects.filter(course=c).count() for c in courses]),
    }
    return render(request, "instructor_dashboard.html", context)


# ===========================
# หน้าแสดงปุ่มชำระเงินแบบง่าย (ถ้าต้องการ)
# ===========================
from django.views import View


class PaymentView(View):
    def get(self, request, course_id):
        course = Course.objects.get(id=course_id)
        return render(request, "payment/payment_form.html", {"course": course})
    

def register(request):
    return redirect("authen:register")
