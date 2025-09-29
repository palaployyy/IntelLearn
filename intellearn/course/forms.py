from django import forms
from .models import Course
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description", "thumbnail_url", "video_url", "price"]

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter course title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Enter course description"}),
            "thumbnail_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "Thumbnail URL (optional)"}),
            "video_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "Video URL (optional)"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0", "placeholder": "Course price"}),
        }

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]