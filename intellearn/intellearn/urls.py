from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from course.views import HomeView   # ✅ import จาก app

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("course.urls")), 
    path("accounts/", include("django.contrib.auth.urls")), # รวม urls ของ app
    path("payment/", include("payment.urls")),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)