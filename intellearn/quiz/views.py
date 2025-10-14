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
