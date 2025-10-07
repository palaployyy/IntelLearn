# from django.db import models
# from django.conf import settings

# อ้างอิง User model จาก accounts
# User = settings.AUTH_USER_MODEL


# class Course(models.Model):
#     instructor = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="courses"
#     )
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     thumbnail_url = models.URLField(blank=True, null=True)
#     video_url = models.URLField(blank=True, null=True)
#     price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     total_lessons = models.PositiveIntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.title} (by {self.instructor})"


# class Lesson(models.Model):
#     course = models.ForeignKey(
#         Course,
#         on_delete=models.CASCADE,
#         related_name="lessons"
#     )
#     title = models.CharField(max_length=255)
#     content = models.TextField(blank=True, null=True)  # ใช้เก็บเนื้อหา text
#     video_url = models.URLField(blank=True, null=True)
#     order = models.PositiveIntegerField(default=1)  # ลำดับบทเรียน
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["order"]

#     def __str__(self):
#         return f"{self.title} (Course: {self.course.title})"


# class Enrollment(models.Model):
#     STATUS_CHOICES = [
#         ("active", "Active"),
#         ("completed", "Completed"),
#         ("dropped", "Dropped"),
#     ]

#     student = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="enrollments"
#     )
#     course = models.ForeignKey(
#         Course,
#         on_delete=models.CASCADE,
#         related_name="enrollments"
#     )
#     enrolled_at = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
#     grade = models.CharField(max_length=255, blank=True, null=True)

    # เก็บว่าเรียน lesson ไหนเสร็จแล้ว (ช่วยทำ progress tracking)
    # completed_lessons = models.ManyToManyField(
    #     Lesson,
    #     blank=True,
    #     related_name="completed_by"
    # )

    # class Meta:
    #     unique_together = ("student", "course")  # ป้องกันสมัครซ้ำ

    # def __str__(self):
    #     return f"{self.student} enrolled in {self.course}"

from django.db import models
from django.conf import settings

class Course(models.Model):
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail_url = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_lessons = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-created_at"]
    def __str__(self): return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=1)
    duration_seconds = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["course", "order"]
        unique_together = ("course", "order")
    def __str__(self): return f"{self.course.title} · {self.order}. {self.title}"

class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        DROPPED = "dropped", "Dropped"
    student = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    grade = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    class Meta:
        unique_together = ("student", "course")
        indexes = [models.Index(fields=["student", "course"])]
    def __str__(self): return f"{self.student} -> {self.course} [{self.status}]"
