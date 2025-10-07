from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.apps import apps

from .forms import PaymentForm
from .models import Payment
from course.models import Course

def _auto_enroll(student, course):
    Enrollment = apps.get_model("course", "Enrollment")
    obj, _ = Enrollment.objects.get_or_create(student=student, course=course, defaults={"status": "active"})
    return obj

@login_required
def checkout(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.student = request.user
            payment.course  = course
            payment.amount  = getattr(course, "price", 0)

            if payment.method == Payment.Method.CREDIT_CARD:
                # MOCK: จ่ายสำเร็จทันที
                payment.status = Payment.Status.PAID
                payment.paid_at = timezone.now()
            else:
                payment.status = Payment.Status.PENDING

            payment.save()

            if payment.paid:
                _auto_enroll(request.user, course)
                messages.success(request, "ชำระเงินสำเร็จ ระบบได้เปิดสิทธิ์เข้าเรียนแล้ว")
            else:
                messages.info(request, "ส่งคำขอชำระแล้ว กรุณารอตรวจสอบสลิป")

            return redirect("payment:success", payment_id=payment.id)
    else:
        form = PaymentForm()

    return render(request, "payment/payment_form.html", {"course": course, "form": form})

@login_required
def success(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)
    return render(request, "payment/payment_success.html", {"payment": payment})

@user_passes_test(lambda u: u.is_staff)
def confirm(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    payment.status = Payment.Status.PAID
    payment.paid_at = timezone.now()
    payment.save()
    _auto_enroll(payment.student, payment.course)
    messages.success(request, "ยืนยันการชำระแล้ว และเปิดสิทธิ์เรียนเรียบร้อย")
    return redirect("admin:payment_payment_changelist")
