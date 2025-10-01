from django.shortcuts import render
from course.models import Course, Enrollment


def instructor_dashboard(request):
    """ Dashboard สำหรับ Instructor """
    courses = Course.objects.filter(instructor=request.user)
    return render(request, "dashboard/instructor_dashboard.html", {
        "courses": courses
    })


def student_dashboard(request):
    """ Dashboard สำหรับ Student """
    enrollments = Enrollment.objects.filter(student=request.user)
    return render(request, "dashboard/student_dashboard.html", {
        "enrollments": enrollments
    })
