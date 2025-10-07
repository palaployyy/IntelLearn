from django.urls import path
from . import views

app_name = "payment"
urlpatterns = [
    path("checkout/<int:course_id>/", views.checkout, name="checkout"),
    path("success/<int:payment_id>/", views.success, name="success"),
    path("confirm/<int:payment_id>/", views.confirm, name="confirm"),  # staff only
]
