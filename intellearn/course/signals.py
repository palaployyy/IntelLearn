# course/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Lesson

def _recount(course):
    course.total_lessons = course.lessons.count()
    course.save(update_fields=["total_lessons"])

@receiver(post_save, sender=Lesson)
def on_lesson_saved(sender, instance, **kwargs): _recount(instance.course)

@receiver(post_delete, sender=Lesson)
def on_lesson_deleted(sender, instance, **kwargs): _recount(instance.course)
