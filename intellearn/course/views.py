from django.views.generic import ListView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Q, Count, Sum
from .models import Course, Enrollment, Lesson
from .forms import CourseForm
from .forms import RegisterForm
from django import forms
from django.views import View


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
    # ❌ ลบเช็ก login ออก
    # ❌ ลบเช็ก is_staff ออก

    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            # ถ้าไม่มี instructor (เพราะ user ไม่ได้ login) → set เป็น None ได้
            if request.user.is_authenticated:
                course.instructor = request.user
            else:
                course.instructor = None  # ✅ ให้ใส่ NULL ได้ (ต้องแก้ model ให้ instructor = null=True ด้วย)
            course.save()
            return redirect("home")
    else:
        form = CourseForm()
    return render(request, "course_form.html", {"form": form, "title": "Add New Course"})



def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)

    # ❌ ลบเช็ก login
    # ❌ ลบเช็กว่าเป็น instructor หรือไม่

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
        context["is_paid"] = False  # เพิ่มตัวแปรใหม่ตรวจสอบสถานะการชำระเงิน

        if user.is_authenticated:
            enrollment = Enrollment.objects.filter(student=user, course=course).first()
            if enrollment:
                context["is_enrolled"] = True

                # ตรวจสอบว่ามีการชำระเงินแล้ว
                payment = Payment.objects.filter(student=user, course=course, status="paid").first()
                if payment:
                    context["is_paid"] = True
        return context

    def post(self, request, *args, **kwargs):
        """ ใช้ตอนกดปุ่ม Enroll """
        course = self.get_object()
        user = request.user

        if not user.is_authenticated:
            return redirect("login")
        
        # ตรวจสอบว่ามีการชำระเงินก่อนการลงทะเบียน
        payment = Payment.objects.filter(student=user, course=course, status="paid").first()
        if not payment:
            messages.error(request, "กรุณาทำการชำระเงินก่อนลงทะเบียน")
            return redirect("payment:checkout", course_id=course.id)  # ไปที่หน้าชำระเงิน

        # ถ้าชำระเงินแล้วลงทะเบียน
        Enrollment.objects.get_or_create(student=user, course=course)
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
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Lesson title"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Lesson content"}),
            "video_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "Video URL"}),
            "order": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Order"}),
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
            return redirect("course_detail", pk=course.id)
    else:
        form = LessonForm()

    return render(request, "lesson_form.html", {"form": form, "title": f"Add Lesson to {course.title}"})


# ✅ แก้ไขบทเรียน
def edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method == "POST":
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            return redirect("course_detail", pk=lesson.course.id)
    else:
        form = LessonForm(instance=lesson)

    return render(request, "lesson_form.html", {"form": form, "title": f"Edit Lesson: {lesson.title}"})


# ✅ ลบบทเรียน
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course_id = lesson.course.id
    lesson.delete()
    return redirect("course_detail", pk=course_id)

class PaymentView(View):
    def get(self, request, course_id):
        course = Course.objects.get(id=course_id)
        return render(request, "payment/payment_form.html", {"course": course})