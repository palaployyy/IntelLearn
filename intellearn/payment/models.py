from django.db import models
from django.conf import settings
from django.utils import timezone
from course.models import Course


class Payment(models.Model):
    # ── Choices ────────────────────────────────────────────────────────────────
    METHOD_TRANSFER = "transfer"
    METHOD_CARD = "credit_card"
    METHOD_PROMPTPAY = "promptpay"

    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_FAILED = "failed"

    METHOD_CHOICES = [
        (METHOD_TRANSFER, "Bank Transfer"),
        (METHOD_CARD, "Credit Card"),
        (METHOD_PROMPTPAY, "PromptPay"),
    ]
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_FAILED, "Failed"),
    ]

    # ── Relations ─────────────────────────────────────────────────────────────
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    # ── Core payment fields ───────────────────────────────────────────────────
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="thb")

    method = models.CharField(
        max_length=20, choices=METHOD_CHOICES, default=METHOD_TRANSFER
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )

    # หลักฐานโอน (โอน/พร้อมเพย์)
    proof = models.ImageField(
        upload_to="payment_proofs/",
        blank=True,
        null=True,
        help_text="Upload slip or proof of payment",
    )

    # อ้างอิง Stripe (กรณีใช้ Stripe Checkout / PaymentIntent)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)  # manual approve (สลิป)
    paid_at = models.DateTimeField(blank=True, null=True)       # เวลาชำระสำเร็จจริง

    # ── Meta ──────────────────────────────────────────────────────────────────
    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["course"]),
            models.Index(fields=["status"]),
        ]

    # ── Helpers ───────────────────────────────────────────────────────────────
    def __str__(self):
        return f"Payment {self.id} - {self.student} - {self.course} ({self.status})"

    @property
    def is_paid(self) -> bool:
        return self.status == self.STATUS_PAID

    def mark_paid(self, when=None, save=True):
        """
        ใช้เมื่อตรวจสอบแล้วว่าชำระสำเร็จ (จาก webhook หรือแอดมินกดยืนยัน)
        """
        self.status = self.STATUS_PAID
        now = when or timezone.now()
        # ถ้ามาจากสลิปอนุมัติ อาจตั้ง confirmed_at ด้วย
        if not self.paid_at:
            self.paid_at = now
        if save:
            self.save(update_fields=["status", "paid_at"])

    def mark_failed(self, save=True):
        self.status = self.STATUS_FAILED
        if save:
            self.save(update_fields=["status"])
