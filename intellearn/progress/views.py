# progress/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from course.models import Lesson, Enrollment
from .models import LearningProgress

@login_required
def mark_done(request, lesson_id: int):
    if request.method != "POST":
        return redirect("course:home")

    lesson = get_object_or_404(Lesson, id=lesson_id)
    # หา enrollment ของผู้ใช้ในคอร์สเดียวกับ lesson
    enrollment = Enrollment.objects.filter(
        student=request.user, course=lesson.course
    ).first()
    if not enrollment:
        # ยังไม่ลงทะเบียน → กลับไปหน้าคอร์ส
        return redirect("course:course_detail", pk=lesson.course_id)

    progress, _ = LearningProgress.objects.get_or_create(enrollment=enrollment)
    progress.completed_lessons.add(lesson)
    progress.save()

    return redirect("course:course_detail", pk=lesson.course_id)

@login_required
def unmark_done(request, lesson_id: int):
    if request.method != "POST":
        return redirect("course:home")

    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment = Enrollment.objects.filter(
        student=request.user, course=lesson.course
    ).first()
    if not enrollment:
        return redirect("course:course_detail", pk=lesson.course_id)

    progress, _ = LearningProgress.objects.get_or_create(enrollment=enrollment)
    progress.completed_lessons.remove(lesson)
    progress.save()

    return redirect("course:course_detail", pk=lesson.course_id)

# (ออปชัน) หน้า list ความคืบหน้าของฉัน
@login_required
def my_progress(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related("course")
    rows = []
    for en in enrollments:
        progress, _ = LearningProgress.objects.get_or_create(enrollment=en)
        rows.append({
            "course": en.course,
            "pct": progress.percentage,
            "done": progress.completed_lessons.count(),
            "total": en.course.lessons.count(),
        })
    return render(request, "progress/my_progress.html", {"rows": rows})
