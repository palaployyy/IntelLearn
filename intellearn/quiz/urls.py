from django.urls import path
from . import views

app_name = "quiz"
urlpatterns = [
    path("<int:quiz_id>/take/", views.take_quiz, name="take"),
    path("<int:quiz_id>/submit/", views.submit_quiz, name="submit"),
    path("add/<int:course_id>/", views.add_quiz, name="add_quiz"),
    path("edit/<int:quiz_id>/", views.edit_quiz, name="edit_quiz"),
    path("question/add/<int:quiz_id>/", views.add_question, name="add_question"),
    path("question/edit/<int:question_id>/", views.edit_question, name="edit_question"),
    path("question/delete/<int:question_id>/", views.delete_question, name="delete_question"),
    path("delete/<int:quiz_id>/", views.delete_quiz, name="delete_quiz"),
    

]
