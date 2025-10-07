from django.db import models
from django.conf import settings

class Payment(models.Model):
    class Method(models.TextChoices):
        TRANSFER = "transfer", "Bank Transfer"
        CREDIT_CARD = "credit_card", "Credit Card"
        PROMPTPAY = "promptpay", "PromptPay"
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    student = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE, related_name="payments")
    course = models.ForeignKey("course.Course",
                               on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.TRANSFER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    proof = models.ImageField(upload_to="payment_proofs/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Payment {self.id} - {self.student} - {self.course} ({self.status})"
    @property
    def paid(self): return self.status == self.Status.PAID
