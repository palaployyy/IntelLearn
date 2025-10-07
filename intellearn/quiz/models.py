from django.db import models
from django.conf import settings

class Quiz(models.Model):
    course = models.ForeignKey("course.Course", on_delete=models.CASCADE, related_name="quizzes")
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    total_questions = models.PositiveIntegerField(default=0)
    pass_score = models.PositiveIntegerField(default=0)  # เปอร์เซ็นต์ 0–100
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.course.title} · {self.title}"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["quiz", "order"]
        unique_together = ("quiz", "order")

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    answer_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Submission(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In progress"
        SUBMITTED = "submitted", "Submitted"
    enrollment = models.ForeignKey("course.Enrollment",
                                   on_delete=models.CASCADE, related_name="submissions")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    passed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    submitted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("enrollment", "quiz")
        indexes = [models.Index(fields=["student", "quiz"])]

class SubmissionAnswer(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="chosen_answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    class Meta:
        unique_together = ("submission", "question")
