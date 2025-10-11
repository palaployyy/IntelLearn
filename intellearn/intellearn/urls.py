# from django.contrib import admin
# from django.urls import path, include
# from course.views import HomeView  # ใช้ในกรณีต้องการหน้าโฮมหลัก
# from django.conf import settings
# from django.conf.urls.static import static

# urlpatterns = [
#     # Admin
#     path("admin/", admin.site.urls),

#     # หน้าโฮมของเว็บไซต์
#     path("", HomeView.as_view(), name="home"),

#     # เส้นทางของ course ทั้งหมด
#     path("course/", include(("course.urls", "course"), namespace="course")),

#     # เส้นทางของ Authen (ระบบล็อกอิน / สมัคร / โปรไฟล์)
#     path("auth/", include(("authen.urls", "authen"), namespace="authen")),


#     # เส้นทางของ Dashboard
#     path("dashboard/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),

#      path("payments/", include(("payment.urls", "payment"), namespace="payment")),

#     # เส้นทางมาตรฐานของ Django Authentication (login/logout/reset password)
#     # path("accounts/", include("django.contrib.auth.urls")),
# ]
# if settings.DEBUG:  # ป้องกัน error ตอน deploy
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# หน้าโฮมหลัก ใช้ HomeView จากแอป course
from course.views import HomeView

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

    # เส้นทางของ Payment (โอน/สลิป + Stripe)
    # ใช้ prefix เป็น 'payment/' ให้ตรงกับตัวอย่างใน views/templates
    path("payment/", include(("payment.urls", "payment"), namespace="payment")),

    # (ออปชัน) เส้นทางของ Quiz ถ้ามีใช้งานหน้า take/submit
    path("quiz/", include(("quiz.urls", "quiz"), namespace="quiz")),
]

# ให้ Django เสิร์ฟไฟล์สื่อ (MEDIA) ระหว่างพัฒนา
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
