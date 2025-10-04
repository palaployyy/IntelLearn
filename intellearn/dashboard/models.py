from django.db import models
from django.conf import settings
from course.models import Course

User = settings.AUTH_USER_MODEL


class StudentDashboard(models.Model):
    student = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_dashboard"
    )
    last_login_at = models.DateTimeField(auto_now=True)
    total_courses = models.PositiveIntegerField(default=0)
    total_progress_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        help_text="ค่าเฉลี่ย % ความคืบหน้าของทุกคอร์ส"
    )
    total_quizzes_passed = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Dashboard for Student: {self.student.username}"


class InstructorDashboard(models.Model):
    instructor = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="instructor_dashboard"
    )
    last_login_at = models.DateTimeField(auto_now=True)
    total_courses_created = models.PositiveIntegerField(default=0)
    total_students = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )

    def __str__(self):
        return f"Dashboard for Instructor: {self.instructor.username}"


class DashboardLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="dashboard_logs"
    )
    action = models.CharField(max_length=255)   # เช่น "view_course", "attempt_quiz"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} did {self.action} at {self.created_at}"
