from django.db import models
from django.conf import settings
from course.models import Course

User = settings.AUTH_USER_MODEL


class Quiz(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="quizzes"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    total_questions = models.PositiveIntegerField(default=0)
    pass_score = models.PositiveIntegerField(default=0)  # เกณฑ์ผ่าน เช่น 50 คะแนน
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions"
    )
    text = models.TextField()
    points = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Q: {self.text[:50]}... (Quiz: {self.quiz.title})"


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers"
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer: {self.text} ({'Correct' if self.is_correct else 'Wrong'})"


class Submission(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="submissions"
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="submissions"
    )
    score = models.PositiveIntegerField(default=0)
    passed = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.quiz} : {self.score} ({'Pass' if self.passed else 'Fail'})"
