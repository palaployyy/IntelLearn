from django.views.generic import ListView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import HttpResponseForbidden
from django.db.models import Q, Count
from django.contrib import messages
from django import forms
from django.views import View

from .models import Course, Enrollment, Lesson
from .forms import CourseForm, RegisterForm
from payment.models import Payment


# ✅ Home Page (ทุกคนเข้าได้ ไม่ต้อง login)
class HomeView(ListView):
    model = Course
    template_name = "home.html"
    context_object_name = "courses"

    def get_queryset(self):
        queryset = Course.objects.annotate(
            lesson_count=Count("lessons"),
            student_count=Count("enrollments"),
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
                    Q(title__icontains=search)
                    | Q(description__icontains=search)
                    | Q(instructor__username__icontains=search)
                )
        return queryset


# ✅ Instructor: Add Course
def add_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            if request.user.is_authenticated:
                course.instructor = request.user
            else:
                course.instructor = None  # ต้องตั้ง null=True ใน model
            course.save()
            return redirect("home")
    else:
        form = CourseForm()
    return render(request, "course_form.html", {"form": form, "title": "Add New Course"})


def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = CourseForm(instance=course)

    return render(
        request, "course_form.html", {"form": form, "title": f"Edit Course: {course.title}"}
    )


# ✅ Student: Course Detail (กดเข้าไปดู/Enroll ได้)
class CourseDetailView(DetailView):
    model = Course
    template_name = "course_detail.html"
    context_object_name = "course"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        user = self.request.user

        # ข้อมูลพื้นฐาน
        context["lessons"] = course.lessons.all().order_by("order", "id")
        context["students_count"] = course.enrollments.count()

        # สถานะผู้ใช้กับคอร์ส
        context["is_enrolled"] = False
        context["is_paid"] = False
        context["progress"] = None

        if user.is_authenticated:
            enrollment = Enrollment.objects.filter(student=user, course=course).first()
            if enrollment:
                context["is_enrolled"] = True
                # เตรียม progress ของผู้ใช้
                progress, _ = LearningProgress.objects.get_or_create(enrollment=enrollment)
                context["progress"] = progress

            # ตรวจสอบการชำระเงินสำเร็จแล้วหรือยัง
            paid = Payment.objects.filter(
                student=user, course=course, status="paid"
            ).exists()
            context["is_paid"] = paid

        # ถ้าโปรเจกต์มี Quiz ที่ FK มาที่ Course แล้วตั้ง related_name="quizzes"
        # ใน template จะใช้: course.quizzes.first --> ปุ่ม Quiz
        return context

    def post(self, request, *args, **kwargs):
        """
        กดปุ่ม Enroll:
        - ต้อง login และต้องจ่ายเงินแล้ว
        """
        course = self.get_object()
        user = request.user

        if not user.is_authenticated:
            return redirect("authen:login")

        # ตรวจสอบการชำระเงิน
        has_paid = Payment.objects.filter(
            student=user, course=course, status="paid"
        ).exists()
        if not has_paid:
            messages.error(request, "กรุณาทำการชำระเงินก่อนลงทะเบียน")
            return redirect("payment:checkout", course_id=course.id)

        Enrollment.objects.get_or_create(student=user, course=course)
        messages.success(request, "ลงทะเบียนคอร์สเรียบร้อยแล้ว")
        return redirect("course:my_courses")

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


# ✅ เพิ่มบทเรียน
def add_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            # 👉 ต้องใส่ namespace 'course:' ให้ตรงกับ include(...)
            return redirect("course:course_detail", pk=course.id)
    else:
        form = LessonForm()

    return render(
        request, "lesson_form.html", {"form": form, "title": f"Add Lesson to {course.title}"}
    )


# ✅ แก้ไขบทเรียน
def edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method == "POST":
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            return redirect("course:course_detail", pk=lesson.course.id)
    else:
        form = LessonForm(instance=lesson)

    return render(
        request, "lesson_form.html", {"form": form, "title": f"Edit Lesson: {lesson.title}"}
    )


# ✅ ลบบทเรียน
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course_id = lesson.course.id
    lesson.delete()
    return redirect("course:course_detail", pk=course_id)


@login_required
def delete_course_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # ✅ ตรวจสอบสิทธิ์
    if course.instructor != request.user:
        messages.error(request, "❌ คุณไม่มีสิทธิ์ลบคอร์สนี้")
        return redirect("course:home")

    if request.method == "POST":
        course.delete()
        messages.success(request, "✅ ลบคอร์สเรียบร้อยแล้ว")
        return redirect("course:home")

    return render(request, "confirm_delete.html", {"course": course})


@login_required
def instructor_dashboard_view(request):
    if not request.user.groups.filter(name="instructor").exists():
        return redirect("course:home")

    # ✅ ดึงเฉพาะคอร์สของ Instructor คนนี้
    courses = Course.objects.filter(instructor=request.user)

    # ✅ รวมข้อมูล enrollment ของคอร์สแต่ละอัน
    course_data = []
    for course in courses:
        enrollments = Enrollment.objects.filter(course=course)
        total_students = enrollments.count()
        completed = enrollments.filter(status="completed").count()
        active = enrollments.filter(status="active").count()
        dropped = enrollments.filter(status="dropped").count()

        course_data.append(
            {
                "course": course,
                "total_students": total_students,
                "completed": completed,
                "active": active,
                "dropped": dropped,
            }
        )

    # ✅ สถิติรวม
    total_courses = courses.count()
    total_students = Enrollment.objects.filter(course__in=courses).count()
    total_revenue = sum([c.price * Enrollment.objects.filter(course=c).count() for c in courses])

    context = {
        "course_data": course_data,
        "total_courses": total_courses,
        "total_students": total_students,
        "total_revenue": total_revenue,
    }

    return render(request, "instructor_dashboard.html", context)


# (ถ้ายังต้องใช้ view นี้อยู่)
class PaymentView(View):
    def get(self, request, course_id):
        course = Course.objects.get(id=course_id)
        return render(request, "payment/payment_form.html", {"course": course})
