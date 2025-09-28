from django.views.generic import ListView
from django.shortcuts import render, redirect, get_object_or_404
from .models import Course 
from .forms import CourseForm
from django.db.models import Q
from django import forms

class HomeView(ListView):
    model = Course
    template_name = "home.html"
    context_object_name = "courses"

    def get_queryset(self):
        queryset = Course.objects.all()
        search = self.request.GET.get("search")
        field = self.request.GET.get("field")

        if search:
            if field == "title":
                queryset = queryset.filter(title__icontains=search)
            elif field == "description":
                queryset = queryset.filter(description__icontains=search)
            elif field == "instructor":
                queryset = queryset.filter(instructor__name__icontains=search)
            else:
                queryset = queryset.filter(
                    Q(title__icontains=search) |
                    Q(description__icontains=search) |
                    Q(instructor__name__icontains=search)
                )
        return queryset

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description", "price", "thumbnail_url", "video_url", "total_lessons"]

# View สำหรับแก้ไขคอร์ส

def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = CourseForm(instance=course)

    return render(request, "course_form.html", {"form": form, "title": f"Edit Course: {course.title}"})


def add_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")  # กลับไปหน้า Home
    else:
        form = CourseForm()

    return render(request, "course_form.html", {"form": form, "title": "Add New Course"})

# class HomePageView(ListView):
#     model = Course
#     template_name = 'home.html'
#     context_object_name = 'courses'
#     paginate_by = 10

#     def get_queryset(self):
#         search_query = self.request.GET.get('search_query', '').strip()  # รับคำค้นจาก URL
#         if search_query:
#             # ค้นหาคอร์สที่มีคำค้นในชื่อคอร์สหรือคำบรรยาย
#             courses = Course.objects.filter(title__icontains=search_query) | Course.objects.filter(description__icontains=search_query)
#         else:
#             courses = Course.objects.all()  # ถ้าไม่มีคำค้นให้แสดงคอร์สทั้งหมด
#         return courses
    
# def create_course(request):
#     if request.method == 'POST':
#         form = CourseForm(request.POST, request.FILES)  # ใช้ request.FILES สำหรับอัปโหลดไฟล์
#         if form.is_valid():
#             form.save()  # บันทึกข้อมูลคอร์สใหม่
#             return redirect('home')  # เปลี่ยนไปหน้า Home หลังจากบันทึกสำเร็จ
#     else:
#         form = CourseForm()
#     return render(request, 'create_course.html', {'form': form})