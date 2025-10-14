from django import forms
from .models import Quiz, Question, Answer

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ["title", "description", "total_questions", "pass_score"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Quiz title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "total_questions": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "pass_score": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text", "points"]
        widgets = {
            "text": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Question text"}),
            "points": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["text", "is_correct"]
        widgets = {
            "text": forms.TextInput(attrs={"class": "form-control", "placeholder": "Answer text"}),
            "is_correct": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
