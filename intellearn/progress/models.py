from django.db import models

class LearningProgress(models.Model):
    enrollment = models.ForeignKey("course.Enrollment",
                                   on_delete=models.CASCADE,
                                   related_name="progress_entries")
    lesson = models.ForeignKey("course.Lesson", on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    last_viewed_at = models.DateTimeField(auto_now=True)
    percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # 0–100 ต่อบท
    class Meta:
        unique_together = ("enrollment", "lesson")
        indexes = [models.Index(fields=["enrollment", "lesson"])]
