from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from course.models import Course, Lesson, Enrollment
from .models import LearningProgress


def _get_or_create_progress(enrollment: Enrollment) -> LearningProgress:
    prog, _ = LearningProgress.objects.get_or_create(enrollment=enrollment)
    return prog


@login_required
def my_progress(request):
    """ความคืบหน้าของคอร์สทั้งหมดที่ผู้ใช้คนนี้ลงทะเบียนอยู่"""
    enrollments = (
        Enrollment.objects
        .filter(student=request.user)
        .select_related("course")
    )

    rows = []
    for e in enrollments:
        prog = _get_or_create_progress(e)
        total = e.course.lessons.count()
        done = prog.completed_lessons.count()
        pct = round((done / total * 100) if total else 0, 2)
        rows.append({"course": e.course, "total": total, "done": done, "pct": pct})

    return render(request, "progress/my_progress.html", {"rows": rows})


@login_required
def course_progress(request, course_id: int):
    """สำหรับ Instructor ดู progress ของนักเรียนในคอร์สนี้"""
    course = get_object_or_404(Course, id=course_id)
    enrollments = (
        Enrollment.objects
        .filter(course=course)
        .select_related("student")
    )

    rows = []
    total = course.lessons.count()
    for e in enrollments:
        prog = _get_or_create_progress(e)
        done = prog.completed_lessons.count()
        pct  = round((done / total * 100) if total else 0, 2)
        rows.append({"student": e.student, "done": done, "total": total, "pct": pct})

    return render(request, "progress/course_progress.html", {"course": course, "rows": rows})


@login_required
def mark_done(request, lesson_id: int):
    """ติ๊กว่าเรียนบทเรียนนี้จบแล้ว"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=lesson.course)
    prog = _get_or_create_progress(enrollment)
    prog.completed_lessons.add(lesson)
    return redirect("course:course_detail", pk=lesson.course.id)


@login_required
def unmark_done(request, lesson_id: int):
    """ยกเลิกติ๊กบทเรียนนี้"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=lesson.course)
    prog = _get_or_create_progress(enrollment)
    prog.completed_lessons.remove(lesson)
    return redirect("course:course_detail", pk=lesson.course.id)
