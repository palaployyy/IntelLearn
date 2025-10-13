# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404, render, redirect
# from django.contrib import messages
# from .models import Quiz, Submission
# from .services import grade_submission
# from course.models import Enrollment

# @login_required
# def take_quiz(request, quiz_id):
#     quiz = get_object_or_404(Quiz.objects.select_related("course"), id=quiz_id)

#     # อนุญาตเฉพาะผู้ลงทะเบียนคอร์ส
#     enrolled = Enrollment.objects.filter(student=request.user, course=quiz.course).exists()
#     if not enrolled:
#         messages.error(request, "คุณต้องลงทะเบียนคอร์สก่อนจึงจะทำแบบทดสอบได้")
#         return redirect("/courses/")

#     questions = quiz.questions.prefetch_related("answers").all()
#     return render(request, "quiz/take_quiz.html", {"quiz": quiz, "questions": questions})

# @login_required
# def submit_quiz(request, quiz_id):
#     if request.method != "POST":
#         return redirect("quiz:take", quiz_id=quiz_id)

#     quiz = get_object_or_404(Quiz, id=quiz_id)

#     # สร้าง/ดึง submission (1 คน/quiz 1 รายการ)
#     submission, _ = Submission.objects.get_or_create(student=request.user, quiz=quiz)
#     # เก็บคำตอบจาก form: name="q-<id>" value="<answer_id>"
#     answers_map = {k.split("-")[1]: v for k, v in request.POST.items() if k.startswith("q-")}
#     grade_submission(submission=submission, answers_map=answers_map)

#     return render(request, "quiz/result.html", {"quiz": quiz, "submission": submission})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Quiz, Answer

def take_quiz(request, quiz_id: int):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all().prefetch_related("answers")
    return render(request, "quiz/take_quiz.html", {"quiz": quiz, "questions": questions})

def submit_quiz(request, quiz_id: int):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all().prefetch_related("answers")

    score = 0
    total = 0
    for q in questions:
        total += q.points
        ans_id = request.POST.get(f"q-{q.id}")
        if not ans_id:
            continue
        try:
            ans = Answer.objects.get(id=ans_id, question=q)
        except Answer.DoesNotExist:
            continue
        if ans.is_correct:
            score += q.points

    passed = score >= quiz.pass_score
    return render(request, "quiz/result.html", {
        "quiz": quiz,
        "score": score,
        "total": total,
        "passed": passed,
    })
