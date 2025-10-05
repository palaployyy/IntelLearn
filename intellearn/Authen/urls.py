# authen/urls.py
from django.urls import path
from .views import login_view, logout_view, register_view, change_password_view

app_name = "authen"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path("password/change/", change_password_view, name="password_change"),
]

