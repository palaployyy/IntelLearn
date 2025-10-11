# payment/views.py
from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import PaymentForm
from .models import Payment
from course.models import Course


def _auto_enroll(student, course):
    """
    เปิดสิทธิ์เข้าเรียนอัตโนมัติหลังชำระเงินสำเร็จ
    """
    Enrollment = apps.get_model("course", "Enrollment")
    obj, _ = Enrollment.objects.get_or_create(
        student=student,
        course=course,
        defaults={"status": "active"},
    )
    return obj


@login_required
def payment_checkout(request, course_id):
    """
    หน้า Checkout (โอน/พร้อมเพย์/บัตรแบบ mock)
    - บัตร (mock) => ชำระสำเร็จทันที, set paid + paid_at แล้ว enroll
    - โอน/พร้อมเพย์ => pending + อัปโหลดสลิป รอแอดมินยืนยัน
    """
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        form = PaymentForm(request.POST, request.FILES, course=course)
        if form.is_valid():
            payment: Payment = form.save(commit=False)
            payment.student = request.user
            payment.course = course
            payment.amount = getattr(course, "price", 0)

            if payment.method == Payment.METHOD_CARD:
                # โหมด MOCK: ถือว่าชำระสำเร็จทันที
                payment.status = Payment.STATUS_PAID
                payment.paid_at = timezone.now()
            else:
                # โอน/PromptPay → pending รอแอดมินตรวจสลิป
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

    return render(
        request,
        "payment/payment_form.html",
        {
            "course": course,
            "form": form,
        },
    )


@login_required
def payment_success(request, payment_id):
    """
    หน้าแสดงสถานะการชำระเงินของรายการที่เพิ่งสร้าง
    """
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)
    return render(request, "payment/payment_success.html", {"payment": payment})


@user_passes_test(lambda u: u.is_staff)
def confirm_payment(request, payment_id):
    """
    สำหรับแอดมินกดยืนยันสลิป:
    - เปลี่ยนสถานะเป็น paid
    - ตั้งเวลาชำระ paid_at (ถ้ายังไม่มี)
    - auto-enroll
    """
    payment = get_object_or_404(Payment, id=payment_id)
    payment.status = Payment.STATUS_PAID
    now = timezone.now()
    payment.confirmed_at = now
    if not payment.paid_at:
        payment.paid_at = now
    payment.save(update_fields=["status", "confirmed_at", "paid_at"])

    _auto_enroll(payment.student, payment.course)
    messages.success(request, "ยืนยันการชำระเงินและเปิดสิทธิ์เรียนเรียบร้อย")

    # กลับไปหน้า changelist ของโมเดล Payment ในแอดมิน
    return redirect("admin:payment_payment_changelist")
