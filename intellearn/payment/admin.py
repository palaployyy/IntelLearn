# payments/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "course", "amount", "method", "status", "created_at", "confirmed_at", "proof_thumb")
    list_filter = ("status", "method", "created_at")
    search_fields = ("student__username", "course__title")

    actions = ["mark_as_paid"]

    def proof_thumb(self, obj):
        if obj.proof:
            return format_html('<img src="{}" style="height:40px;border-radius:6px" />', obj.proof.url)
        return "-"

    @admin.action(description="ยืนยันการชำระเงิน (mark as paid)")
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status="paid")
        self.message_user(request, f"อัปเดต {updated} รายการเป็น paid แล้ว")
