from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.urls import reverse_lazy
from .forms import RegisterForm


User = get_user_model()

# -------------------------------
# Login View
# -------------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # ✅ redirect ไปหน้า Course แทน dashboard
            return redirect("course:home")

        else:
            messages.error(request, "❌ Username or password invalid")
    return render(request, "authen/login.html")




# -------------------------------
# Logout View
# -------------------------------
def logout_view(request):
    logout(request)
    return render(request, "authen/logout.html")


# -------------------------------
# Register View
# -------------------------------
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
        else:
            user = User.objects.create_user(username=username, email=email, password=password, role=role)
            messages.success(request, "Account created successfully! Please log in.")
            return redirect("authen:login")


    return render(request, "authen/register.html")


# -------------------------------
# Change Password View
# -------------------------------
@login_required
def change_password_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "✅ Password changed successfully.")
            # เดิม: return redirect("change_password")
            return redirect("authen:change_password")  # หรือส่งไปหน้า done: redirect("authen:password_change_done")
        else:
            messages.error(request, "❌ Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "authen/change_password.html", {"form": form})


@login_required
def profile_view(request):
    return render(request, "authen/profile.html")