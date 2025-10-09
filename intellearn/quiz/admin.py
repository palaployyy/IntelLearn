from django.contrib import admin
from .models import Quiz, Question, Answer, Submission

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2

class QuestionAdmin(admin.ModelAdmin):
    list_display = ("quiz", "short_text", "points")
    inlines = [AnswerInline]
    def short_text(self, obj): return (obj.text[:60] + "…") if len(obj.text) > 60 else obj.text

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "total_questions", "pass_score", "created_at")
    search_fields = ("title", "course__title")

admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(Submission)
