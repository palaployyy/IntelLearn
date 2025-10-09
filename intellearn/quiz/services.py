from django.db import transaction
from django.utils import timezone
from .models import Quiz, Question, Answer, Submission

@transaction.atomic
def grade_submission(*, submission: Submission, answers_map: dict[str, int]) -> Submission:
    """
    answers_map: {"<question_id>": <answer_id>, ...}
    """
    total_score = 0
    total_points = 0

    questions = Question.objects.filter(quiz=submission.quiz).prefetch_related("answers")
    for q in questions:
        total_points += q.points
        chosen_id = int(answers_map.get(str(q.id), 0) or 0)
        if chosen_id:
            try:
                chosen = next(a for a in q.answers.all() if a.id == chosen_id)
            except StopIteration:
                chosen = None
            if chosen and chosen.is_correct:
                total_score += q.points

    submission.score = total_score
    # คิดเป็นเปอร์เซ็นต์เทียบ pass_score ที่ตั้งไว้ใน Quiz (0–100)
    percent = round((total_score / total_points) * 100, 2) if total_points else 0
    submission.passed = percent >= submission.quiz.pass_score
    submission.submitted_at = timezone.now()
    submission.save(update_fields=["score", "passed", "submitted_at"])
    return submission
