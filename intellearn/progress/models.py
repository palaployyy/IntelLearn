from django.db import models
from django.conf import settings
from course.models import Course, Lesson, Enrollment

User = settings.AUTH_USER_MODEL


class LearningProgress(models.Model):
    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="progress"
    )
    completed_lessons = models.ManyToManyField(
        Lesson,
        blank=True,
        related_name="progress_records"
    )
    last_accessed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Progress of {self.enrollment.student} in {self.enrollment.course}"

    @property
    def percentage(self):
        """คำนวณเปอร์เซ็นต์ความคืบหน้าการเรียน"""
        total_lessons = self.enrollment.course.lessons.count()
        if total_lessons == 0:
            return 0
        return round((self.completed_lessons.count() / total_lessons) * 100, 2)

