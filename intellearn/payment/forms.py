# payment/forms.py
from __future__ import annotations
from django import forms
from django.core.exceptions import ValidationError
from .models import Payment

# ✅ อนุญาตเฉพาะไฟล์ภาพ
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def _guess_content_type(file_obj) -> str:
    """พยายามเดา content_type จากชื่อไฟล์ ถ้าไม่มี"""
    ct = getattr(file_obj, "content_type", "") or ""
    if ct:
        return ct.lower()
    name = getattr(file_obj, "name", "") or ""
    ext = (name[name.rfind(".") :].lower()) if "." in name else ""
    if ext in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if ext == ".png":
        return "image/png"
    if ext == ".webp":
        return "image/webp"
    return ""


class PaymentForm(forms.ModelForm):
    # mock fields สำหรับทดสอบบัตรเครดิต
    cardholder_name = forms.CharField(required=False, label="Cardholder Name")
    card_number = forms.CharField(required=False, label="Card Number")
    expiration = forms.CharField(required=False, label="Expiration Date (MM/YY)")
    cvv = forms.CharField(required=False, label="CVV")

    class Meta:
        model = Payment
        fields = ["method", "proof"]
        widgets = {
            "method": forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop("course", None)
        super().__init__(*args, **kwargs)
        if not self.initial.get("method"):
            self.initial["method"] = Payment.METHOD_TRANSFER

    def clean(self):
        cleaned = super().clean()
        method = cleaned.get("method") or Payment.METHOD_TRANSFER
        proof = cleaned.get("proof")

        # 🧾 ตรวจสอบกรณีโอนหรือพร้อมเพย์
        if method in (Payment.METHOD_TRANSFER, Payment.METHOD_PROMPTPAY):
            if not proof:
                self.add_error("proof", "กรุณาอัปโหลดสลิปเพื่อยืนยันการชำระเงิน")
            else:
                size = getattr(proof, "size", 0)
                if size > 5 * 1024 * 1024:
                    self.add_error("proof", "ไฟล์ต้องไม่เกิน 5MB")

                ctype = _guess_content_type(proof)
                if ctype not in ALLOWED_IMAGE_TYPES:
                    name = getattr(proof, "name", "") or ""
                    ok_by_ext = any(name.lower().endswith(ext) for ext in ALLOWED_EXTS)
                    if not ok_by_ext:
                        self.add_error("proof", "รองรับเฉพาะไฟล์รูป JPG/PNG/WEBP")

        # 💳 ตรวจสอบ mock card
        if method == Payment.METHOD_CARD:
            missing = []
            for f in ("cardholder_name", "card_number", "expiration", "cvv"):
                if not (self.data.get(f) or "").strip():
                    missing.append(f)
            if missing:
                raise ValidationError("กรุณากรอกข้อมูลบัตรให้ครบเพื่อทดสอบการชำระเงินแบบ mock")

            card = (self.data.get("card_number") or "").replace(" ", "")
            if not card.isdigit() or len(card) not in (15, 16):
                self.add_error("card_number", "เลขบัตรควรเป็นตัวเลข 15–16 หลัก (4242 4242 4242 4242 สำหรับทดสอบ)")
            exp = (self.data.get("expiration") or "").strip()
            if "/" not in exp or len(exp) < 4:
                self.add_error("expiration", "กรุณากรอกในรูปแบบ MM/YY")
            cvv = (self.data.get("cvv") or "").strip()
            if not cvv.isdigit() or len(cvv) not in (3, 4):
                self.add_error("cvv", "CVV ควรเป็นตัวเลข 3–4 หลัก")

        return cleaned
