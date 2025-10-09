# from django.contrib import admin
# from django.urls import path, include
# from course.views import HomeView   # ✅ import จาก app
# from Authen.views import logout_view 

# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path("", include(("course.urls", "course"), namespace="course")),
#     path("accounts/", include("django.contrib.auth.urls")), # รวม urls ของ app
#     path("dashboard/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),
#     path('auth/', include('Authen.urls')),
#     path('course/', include('course.urls')),
#     path("auth/", include(("Authen.urls", "authen"), namespace="authen")),
#     path("accounts/logout/", logout_view, name="accounts_logout"),
#     path("accounts/", include("django.contrib.auth.urls")),


    # path("payments/", include("payments.urls")),
# ]


from django.contrib import admin
from django.urls import path, include
from course.views import HomeView  # ใช้ในกรณีต้องการหน้าโฮมหลัก

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # หน้าโฮมของเว็บไซต์
    path("", HomeView.as_view(), name="home"),

    # เส้นทางของ course ทั้งหมด
    path("course/", include(("course.urls", "course"), namespace="course")),

    # เส้นทางของ Authen (ระบบล็อกอิน / สมัคร / โปรไฟล์)
    path("auth/", include(("authen.urls", "authen"), namespace="authen")),


    # เส้นทางของ Dashboard
    path("dashboard/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),

     path("payments/", include(("payment.urls", "payment"), namespace="payment")),

    # เส้นทางมาตรฐานของ Django Authentication (login/logout/reset password)
    # path("accounts/", include("django.contrib.auth.urls")),
]
