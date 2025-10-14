from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Quiz, Question, Answer
from .forms import QuizForm, QuestionForm, AnswerForm
from course.models import Course

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

@login_required
def add_quiz(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user != course.instructor and not request.user.is_superuser:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์เพิ่มควิซในคอร์สนี้")

    if request.method == "POST":
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.course = course
            quiz.save()
            messages.success(request, "✅ สร้างควิซเรียบร้อยแล้ว")
            return redirect("quiz:edit_quiz", quiz.id)
    else:
        form = QuizForm()

    return render(request, "quiz/quiz_form.html", {"form": form, "title": f"Add Quiz to {course.title}"})


@login_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.user != quiz.course.instructor and not request.user.is_superuser:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์แก้ไขควิซนี้")

    if request.method == "POST":
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ บันทึกควิซเรียบร้อยแล้ว")
            return redirect("course:course_detail", quiz.course.id)
    else:
        form = QuizForm(instance=quiz)

    # 💡 จุดสำคัญคือส่ง quiz เข้า context ด้วย
    return render(
        request,
        "quiz/edit_quiz.html",
        {
            "form": form,
            "quiz": quiz,   # ✅ ต้องมี
            "title": f"Edit Quiz: {quiz.title}",
        },
    )




# -------------------------
# ➕ Add Question
# -------------------------
@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.course  # ✅ ดึง course จาก quiz
    
    # ✅ ตรวจสอบสิทธิ์
    if request.user != course.instructor and not request.user.is_superuser:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์เพิ่มคำถามในควิซนี้")

    if request.method == "POST":
        q_form = QuestionForm(request.POST)
        if q_form.is_valid():
            question = q_form.save(commit=False)
            question.quiz = quiz
            question.save()

            # ✅ สร้างคำตอบเปล่า 4 ตัวเลือกเริ่มต้น
            for i in range(1, 5):
                Answer.objects.create(question=question, text=f"ตัวเลือก {i}")

            messages.success(request, "✅ เพิ่มคำถามเรียบร้อยแล้ว")
            # 🔁 กลับไปหน้า course_detail ของคอร์สนี้
            return redirect("course:course_detail", pk=course.id)
    else:
        q_form = QuestionForm()

    return render(
        request,
        "quiz/question_form.html",
        {"form": q_form, "title": f"Add Question to {quiz.title}", "quiz": quiz, "course": course},
    )

# -------------------------
# ✏️ Edit Question + Answers
# -------------------------
@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    quiz = question.quiz
    course = quiz.course

    if request.user != course.instructor and not request.user.is_superuser:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์แก้ไขคำถามนี้")

    answers = question.answers.all()  # ดึง 4 ตัวเลือกที่สร้างอัตโนมัติ

    if request.method == "POST":
        q_form = QuestionForm(request.POST, instance=question)
        if q_form.is_valid():
            q_form.save()

            # ✅ อัปเดตข้อความตัวเลือกและข้อที่ถูกต้อง
            for ans in answers:
                ans.text = request.POST.get(f"answer_{ans.id}", ans.text)
                ans.is_correct = f"correct_{ans.id}" in request.POST
                ans.save()

            messages.success(request, "✅ บันทึกคำถามและตัวเลือกเรียบร้อยแล้ว")
            return redirect("course:course_detail", pk=course.id)
    else:
        q_form = QuestionForm(instance=question)

    return render(
        request,
        "quiz/edit_question.html",
        {"question": question, "q_form": q_form, "answers": answers, "quiz": quiz, "course": course},
    )

@login_required
def delete_question(request, question_id):
    """Instructor หรือตัวผู้สร้างคอร์สเท่านั้นที่สามารถลบคำถามได้"""
    question = get_object_or_404(Question, id=question_id)
    quiz = question.quiz
    course = quiz.course

    # ✅ ตรวจสอบสิทธิ์
    if request.user != course.instructor and not request.user.is_superuser:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์ลบคำถามนี้")

    if request.method == "POST":
        question.delete()
        messages.success(request, f"🗑️ ลบคำถามจากควิซ '{quiz.title}' แล้ว")
        return redirect("quiz:edit_quiz", quiz.id)

    # ถ้ายังไม่ได้กดยืนยัน
    return render(request, "quiz/confirm_delete_question.html", {"question": question, "quiz": quiz})

@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.course

    if request.user != course.instructor and not request.user.is_superuser:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์ลบควิซนี้")

    if request.method == "POST":
        quiz.delete()
        messages.success(request, f"🗑️ ลบควิซ '{quiz.title}' แล้วเรียบร้อย")
        return redirect("course:course_detail", pk=course.id)

    return render(request, "quiz/confirm_delete_quiz.html", {"quiz": quiz, "course": course})

@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    quiz = question.quiz
    course = quiz.course

    if request.user != course.instructor and not request.user.is_superuser:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์แก้ไขคำถามนี้")

    answers = question.answers.all()  # ดึง 4 ตัวเลือกจากฐานข้อมูล

    if request.method == "POST":
        q_form = QuestionForm(request.POST, instance=question)
        if q_form.is_valid():
            q_form.save()

            # ✅ อัปเดตข้อความและข้อที่ถูกต้อง
            for ans in answers:
                ans.text = request.POST.get(f"answer_{ans.id}", ans.text)
                ans.is_correct = f"correct_{ans.id}" in request.POST
                ans.save()

            messages.success(request, "✅ บันทึกคำถามและตัวเลือกเรียบร้อยแล้ว")
            return redirect("course:course_detail", pk=course.id)
    else:
        q_form = QuestionForm(instance=question)

    return render(
        request,
        "quiz/edit_question.html",
        {"question": question, "q_form": q_form, "answers": answers, "quiz": quiz, "course": course},
    )