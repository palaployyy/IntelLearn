from django.db import models
from django.conf import settings
from course.models import Course


class Payment(models.Model):
    METHOD_CHOICES = [
        ("transfer", "Bank Transfer"),
        ("credit_card", "Credit Card"),
        ("promptpay", "PromptPay"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default="transfer")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    proof = models.ImageField(
        upload_to="payment_proofs/",
        blank=True,
        null=True,
        help_text="Upload slip or proof of payment"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Payment {self.id} - {self.student} - {self.course} ({self.status})"
