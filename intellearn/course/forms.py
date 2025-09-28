from django import forms
from .models import Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description", "thumbnail_url", "video_url", "price", "total_lessons"]

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter course title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Enter course description"}),
            "thumbnail_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "Thumbnail URL"}),
            "video_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "Video URL"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Course price"}),
            "total_lessons": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Total lessons"}),
        }
