# payment/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from .models import Payment

@receiver(post_save, sender=Payment)
def enroll_when_paid(sender, instance: Payment, **kwargs):
    if instance.status == Payment.Status.PAID:
        Enrollment = apps.get_model("course", "Enrollment")
        Enrollment.objects.get_or_create(
            student=instance.student,
            course=instance.course,
            defaults={"status": "active"},
        )
