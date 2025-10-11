# payment/urls.py
from django.urls import path
from . import views

app_name = "payment"

urlpatterns = [
    # --- โอน/พร้อมเพย์/บัตรแบบ mock ---
    path("checkout/<int:course_id>/", views.payment_checkout, name="checkout"),
    path("success/<int:payment_id>/", views.payment_success, name="success"),
    path("confirm/<int:payment_id>/", views.confirm_payment, name="confirm"),

    # --- Stripe (ทดสอบ) ---
    # เริ่มสร้าง Stripe Checkout Session แล้ว redirect ไปหน้าชำระของ Stripe
    path("checkout/<int:course_id>/start/", views.create_checkout_session, name="create_checkout"),
    # รับ Webhook จาก Stripe เพื่อเปลี่ยนสถานะเป็น paid + auto-enroll
    path("webhook/stripe/", views.stripe_webhook, name="stripe_webhook"),
]
