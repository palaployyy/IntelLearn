from django.urls import path
from . import views

app_name = "quiz"
urlpatterns = [
    path("<int:quiz_id>/take/", views.take_quiz, name="take"),
    path("<int:quiz_id>/submit/", views.submit_quiz, name="submit"),
]
