# payment/views.py
from decimal import Decimal

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

import stripe

from course.models import Course
from .forms import PaymentForm
from .models import Payment


# --------- helper ---------
def _auto_enroll(student, course):
    """เปิดสิทธิ์เข้าเรียนทันทีเมื่อตรวจว่าชำระสำเร็จ"""
    Enrollment = apps.get_model("course", "Enrollment")
    Enrollment.objects.get_or_create(student=student, course=course, defaults={"status": "active"})


def _set_if_field(model_obj, **fields):
    """ใส่ค่าเฉพาะ field ที่มีอยู่จริงใน model เพื่อกัน error ต่างเวอร์ชัน schema"""
    for name, value in fields.items():
        if hasattr(model_obj, name):
            setattr(model_obj, name, value)


# --------- 1) โอน/อัปสลิป (mock/manual) ---------
@login_required
def payment_checkout(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = PaymentForm(request.POST, request.FILES, course=course)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.student = request.user
            payment.course = course
            payment.amount = getattr(course, "price", Decimal("0.00"))
            if payment.method == Payment.METHOD_CARD:
                payment.status = Payment.STATUS_PAID
                payment.confirmed_at = timezone.now()
            else:
                payment.status = Payment.STATUS_PENDING
            payment.save()
            if payment.status == Payment.STATUS_PAID:
                _auto_enroll(request.user, course)
                messages.success(request, "ชำระเงินสำเร็จ! ระบบได้เปิดสิทธิ์เข้าเรียนแล้ว")
            else:
                messages.info(request, "ส่งคำขอชำระเงินแล้ว กรุณารอการตรวจสอบสลิป")
            return redirect("payment:success", payment_id=payment.id)
    else:
        form = PaymentForm(course=course)
    return render(request, "payment/payment_form.html", {"course": course, "form": form})


# --------- 2) Stripe Checkout ---------
@login_required
def create_checkout_session(request: HttpRequest, course_id: int):
    """
    สร้าง Stripe Checkout Session แล้ว redirect ไปยัง Stripe
    success_url -> payment:success (อ้างอิง payment_id)
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    if not getattr(settings, "STRIPE_SECRET_KEY", ""):
        return JsonResponse({"error": "Stripe secret key is not set"}, status=500)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    course = get_object_or_404(Course, id=course_id)

    # สร้าง payment record ไว้ก่อน
    payment = Payment.objects.create(
        student=request.user,
        course=course,
        amount=getattr(course, "price", Decimal("0.00")),
        method=Payment.METHOD_CARD,
        status=Payment.STATUS_PENDING,
    )
    _set_if_field(payment, currency="thb")
    payment.save(update_fields=["status"] + (["currency"] if hasattr(payment, "currency") else []))

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

        # เก็บ session_id ไว้ ถ้าโมเดลมี field
        _set_if_field(payment, stripe_session_id=session.id)
        payment.save()

        # ส่งกลับเป็น redirect (เรียกจาก form)
        return redirect(session.url)

    except Exception as e:
        payment.delete()
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def payment_success(request: HttpRequest, payment_id: int):
    """
    หน้าสรุปผลหลังกลับจาก Stripe หรือ manual
    template: payment/payment_success.html / payment/payment_pending.html
    """
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)
    course = payment.course

    # ถ้ามี stripe_session_id จะลองตรวจสอบสถานะจาก Stripe อีกรอบ (optional)
    session_id = getattr(payment, "stripe_session_id", None)
    if session_id and getattr(settings, "STRIPE_SECRET_KEY", ""):
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == "paid" and payment.status != Payment.STATUS_PAID:
                payment.status = Payment.STATUS_PAID
                _set_if_field(payment, paid_at=timezone.now())
                payment.save(update_fields=["status"] + (["paid_at"] if hasattr(payment, "paid_at") else []))
                _auto_enroll(payment.student, course)
        except Exception:
            # ถ้าดึง Stripe ล้มเหลวก็แสดงตามสถานะในฐานข้อมูล
            pass

    if payment.status == Payment.STATUS_PAID or getattr(payment, "is_paid", False):
        return render(request, "payment/payment_success.html", {"payment": payment, "course": course})

    return render(request, "payment/payment_pending.html", {"payment": payment, "course": course})


@user_passes_test(lambda u: u.is_staff)
def confirm_payment(request: HttpRequest, payment_id: int):
    """
    แอดมินกดอนุมัติสลิป -> เปลี่ยนเป็น paid + enroll
    """
    payment = get_object_or_404(Payment, id=payment_id)
    now = timezone.now()
    payment.status = Payment.STATUS_PAID
    _set_if_field(payment, confirmed_at=now, paid_at=getattr(payment, "paid_at", None) or now)
    payment.save()

    _auto_enroll(payment.student, payment.course)
    messages.success(request, "ยืนยันการชำระเงินและเปิดสิทธิ์เรียนเรียบร้อย")
    return redirect("admin:payment_payment_changelist")


# --------- 3) Stripe Webhook (แนะนำรัน stripe listen ตอน dev) ---------
@csrf_exempt
def stripe_webhook(request: HttpRequest):
    """
    รับ event จาก Stripe แล้ว mark payment เป็น paid
    """
    secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")
    if not secret:
        return HttpResponse("Webhook secret not set", status=500)

    payload = request.body
    sig = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig, secret)
    except stripe.error.SignatureVerificationError:
        return HttpResponse("Invalid signature", status=400)
    except Exception:
        return HttpResponse(status=400)

    if event.get("type") == "checkout.session.completed":
        data = event["data"]["object"]
        payment_id = (data.get("metadata") or {}).get("payment_id")
        if payment_id:
            try:
                payment = Payment.objects.get(id=payment_id)
            except Payment.DoesNotExist:
                payment = None
            if payment and payment.status != Payment.STATUS_PAID:
                payment.status = Payment.STATUS_PAID
                _set_if_field(payment, paid_at=timezone.now())
                payment.save(update_fields=["status"] + (["paid_at"] if hasattr(payment, "paid_at") else []))
                _auto_enroll(payment.student, payment.course)

    return HttpResponse(status=200)
