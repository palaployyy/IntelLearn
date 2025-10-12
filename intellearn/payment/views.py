# payment/views.py
from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.conf import settings

from .forms import PaymentForm
from .models import Payment
from course.models import Course

import stripe
from decimal import Decimal


def _auto_enroll(student, course):
    """เปิดสิทธิ์เข้าเรียนอัตโนมัติหลังชำระเงินสำเร็จ"""
    Enrollment = apps.get_model("course", "Enrollment")
    obj, _ = Enrollment.objects.get_or_create(
        student=student, course=course, defaults={"status": "active"}
    )
    return obj


# --------------------------
# 1) โอน/พร้อมเพย์/บัตร (mock)
# --------------------------
@login_required
def payment_checkout(request: HttpRequest, course_id: int):
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        form = PaymentForm(request.POST, request.FILES, course=course)
        if form.is_valid():
            payment: Payment = form.save(commit=False)
            payment.student = request.user
            payment.course = course
            payment.amount = getattr(course, "price", Decimal("0.00"))

            if payment.method == Payment.METHOD_CARD:
                # MOCK: ถือว่าชำระสำเร็จทันที
                payment.status = Payment.STATUS_PAID
                payment.paid_at = timezone.now()
            else:
                # โอน/PromptPay → pending รอแอดมินอนุมัติ
                payment.status = Payment.STATUS_PENDING

            payment.save()

            if payment.is_paid:
                _auto_enroll(request.user, course)
                messages.success(request, "ชำระเงินสำเร็จ! ระบบได้เปิดสิทธิ์เข้าเรียนแล้ว")
            else:
                messages.info(request, "ส่งคำขอชำระเงินแล้ว กรุณารอการตรวจสอบสลิป")

            return redirect("payment:success", payment_id=payment.id)
    else:
        form = PaymentForm(course=course)

    return render(request, "payment/payment_form.html", {"course": course, "form": form})


@login_required
def payment_success(request, payment_id: int):
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)
    return render(request, "payment/payment_success.html", {"payment": payment})


@user_passes_test(lambda u: u.is_staff)
def confirm_payment(request, payment_id: int):
    payment = get_object_or_404(Payment, id=payment_id)
    now = timezone.now()
    payment.status = Payment.STATUS_PAID
    payment.confirmed_at = now
    if not payment.paid_at:
        payment.paid_at = now
    payment.save(update_fields=["status", "confirmed_at", "paid_at"])

    _auto_enroll(payment.student, payment.course)
    messages.success(request, "ยืนยันการชำระเงินและเปิดสิทธิ์เรียนเรียบร้อย")
    return redirect("admin:payment_payment_changelist")


# --------------------------
# 2) Stripe Checkout (ทดสอบ)
# --------------------------

@login_required
def create_checkout_session(request, course_id: int):
    """
    สร้าง Stripe Checkout Session แล้ว
    - ถ้ามาจาก form POST ปกติ -> redirect ไป session.url ทันที
    - ถ้าคาดหวัง JSON (เช่น fetch) -> คืน {"url": "..."}
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    if not settings.STRIPE_SECRET_KEY:
        return JsonResponse({"error": "Stripe secret key is not set"}, status=500)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    course = get_object_or_404(Course, id=course_id)

    payment = Payment.objects.create(
        student=request.user,
        course=course,
        amount=getattr(course, "price", Decimal("0.00")),
        method=Payment.METHOD_CARD,
        status=Payment.STATUS_PENDING,
    )

    amount_int = int(Decimal(payment.amount) * 100)

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "thb",
                    "product_data": {"name": course.title},
                    "unit_amount": amount_int,
                },
                "quantity": 1,
            }],
            metadata={"payment_id": str(payment.id)},
            success_url=f"{settings.SITE_URL}{reverse('payment:success', kwargs={'payment_id': payment.id})}",
            cancel_url=f"{settings.SITE_URL}{reverse('course:course_detail', kwargs={'pk': course.id})}",
        )

        # ถ้ามาจาก form ปกติ -> redirect เลย (ง่าย/เสถียรกว่า)
        accept = request.headers.get("Accept", "")
        if "application/json" not in accept:
            return redirect(session.url)

        # กรณีเรียกด้วย fetch -> คืน JSON
        return JsonResponse({"url": session.url})

    except Exception as e:
        payment.delete()
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def stripe_webhook(request: HttpRequest):
    """
    รับ event จาก Stripe แล้ว mark payment เป็น paid + auto-enroll
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    secret = settings.STRIPE_WEBHOOK_SECRET or ""

    if not secret:
        return HttpResponse("Webhook secret not set", status=500)

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, secret)
    except stripe.error.SignatureVerificationError:
        return HttpResponse("Invalid signature", status=400)
    except Exception:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {}) or {}
        payment_id = metadata.get("payment_id")
        if payment_id:
            try:
                payment = Payment.objects.get(id=payment_id)
                if not payment.is_paid:
                    payment.status = Payment.STATUS_PAID
                    payment.paid_at = timezone.now()
                    payment.save(update_fields=["status", "paid_at"])
                    _auto_enroll(payment.student, payment.course)
            except Payment.DoesNotExist:
                pass

    return HttpResponse(status=200)
