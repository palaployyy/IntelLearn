from django.views.generic import ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count 
from django.contrib.auth.decorators import login_required
from .models import Course
from .forms import CourseForm
from django.views.generic import DetailView
from django.contrib.auth import login
from .forms import RegisterForm

class HomeView(ListView):
    model = Course
    template_name = "home.html"
    context_object_name = "courses"

    def get_queryset(self):
        queryset = Course.objects.all().annotate(
            lesson_count=Count("lessons", distinct=True),
            student_count=Count("enrollments", distinct=True)
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

@login_required
def add_course(request):
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

@login_required
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk, instructor=request.user)
    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = CourseForm(instance=course)
    return render(request, "course_form.html", {"form": form, "title": f"Edit Course: {course.title}"})


class CourseDetailView(DetailView):
    model = Course
    template_name = "course_detail.html"
    context_object_name = "course"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ดึงบทเรียนทั้งหมดของคอร์สนี้
        context["lessons"] = self.object.lessons.all().order_by("order")
        # จำนวนนักเรียน
        context["students_count"] = self.object.enrollments.count()
        return context
    
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # ✅ login อัตโนมัติหลังสมัคร
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})