from django.contrib import admin
from .models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "instructor", "price", "created_at")
    search_fields = ("title", "instructor__name")  # สำหรับการค้นหาคอร์ส
    list_filter = ("instructor", "price")  # ฟิลเตอร์คอร์สตามผู้สอนและราคา
