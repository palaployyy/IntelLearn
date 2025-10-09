from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Quiz, Question

def _recount(quiz: Quiz):
    Quiz.objects.filter(pk=quiz.pk).update(total_questions=quiz.questions.count())

@receiver(post_save, sender=Question)
def on_q_saved(sender, instance, **kwargs): _recount(instance.quiz)

@receiver(post_delete, sender=Question)
def on_q_deleted(sender, instance, **kwargs): _recount(instance.quiz)
