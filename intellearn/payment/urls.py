# payments/urls.py
from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("checkout/<int:course_id>/", views.payment_checkout, name="checkout"),
    path("success/<int:payment_id>/", views.payment_success, name="success"),
    path("confirm/<int:payment_id>/", views.confirm_payment, name="confirm"),
]
