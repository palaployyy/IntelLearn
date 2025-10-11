from django.shortcuts import render

# Create your views here.
# payments/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.apps import apps

from .forms import PaymentForm
from .models import Payment
from course.models import Course  # ปรับเส้นทาง import ให้ตรงโปรเจกต์คุณ

def _auto_enroll(student, course):
    """
    เปิดสิทธิ์เข้าเรียนอัตโนมัติหลังชำระเงินสำเร็จ
    ปรับ app_label และ field ให้ตรงกับโมเดลของคุณถ้าไม่ใช่ 'course.Enrollment'
    """
    Enrollment = apps.get_model("course", "Enrollment")
    obj, created = Enrollment.objects.get_or_create(
        student=student, course=course,
        defaults={"status": "active"}
    )
    return obj

@login_required
def payment_checkout(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = PaymentForm(request.POST, request.FILES, course=course)
        if form.is_valid():
            payment: Payment = form.save(commit=False)
            payment.student = request.user
            payment.course = course
            payment.amount = getattr(course, "price", 0)

            if payment.method == "credit_card":
                # MOCK: ถือว่าชำระสำเร็จทันที
                payment.status = "paid"
                payment.confirmed_at = timezone.now()
            else:
                # โอน/PromptPay → pending รอแอดมินกดอนุมัติ
                payment.status = "pending"

            payment.save()

            if payment.status == "paid":
                _auto_enroll(request.user, course)
                messages.success(request, "ชำระเงินสำเร็จ! ระบบได้เปิดสิทธิ์เข้าเรียนแล้ว")
                return redirect("payments:success", payment_id=payment.id)

            messages.info(request, "ส่งคำขอชำระเงินแล้ว กรุณารอการตรวจสอบสลิป")
            return redirect("payments:success", payment_id=payment.id)
    else:
        form = PaymentForm(course=course)

    return render(request, "payment_form.html", {
        "course": course,
        "form": form,
    })

@login_required
def payment_success(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)
    return render(request, "payments/payment_success.html", {"payment": payment})

# สำหรับแอดมินกดยืนยันสลิป
@user_passes_test(lambda u: u.is_staff)
def confirm_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    payment.status = "paid"
    payment.confirmed_at = timezone.now()
    payment.save()
    _auto_enroll(payment.student, payment.course)
    messages.success(request, "ยืนยันการชำระเงินและเปิดสิทธิ์เรียบร้อย")
    return redirect("admin:payments_payment_changelist")


