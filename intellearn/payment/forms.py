# payments/forms.py
from django import forms
from .models import Payment

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

class PaymentForm(forms.ModelForm):
    # ฟิลด์ mock สำหรับบัตรเครดิต (ไม่ถูกบันทึกลงฐานข้อมูล)
    cardholder_name = forms.CharField(required=False, label="Cardholder Name")
    card_number = forms.CharField(required=False, label="Card Number")
    expiration = forms.CharField(required=False, label="Expiration Date (MM/YY)")
    cvv = forms.CharField(required=False, label="CVV")

    class Meta:
        model = Payment
        fields = ["method", "proof"]  # amount/student/course จะเซ็ตใน view

        widgets = {
            "method": forms.RadioSelect(choices=Payment.METHOD_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop("course", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        method = cleaned.get("method") or "transfer"
        proof = cleaned.get("proof")

        # ถ้าเป็นโอน/PromptPay ต้องมีสลิป
        if method in ("transfer", "promptpay") and not proof:
            self.add_error("proof", "กรุณาอัปโหลดสลิปเพื่อยืนยันการชำระเงิน")

        # ตรวจสอบไฟล์สลิป
        if proof:
            if proof.size > 5 * 1024 * 1024:
                self.add_error("proof", "ไฟล์ต้องไม่เกิน 5MB")
            if getattr(proof, "content_type", "") not in ALLOWED_IMAGE_TYPES:
                self.add_error("proof", "รองรับเฉพาะ JPG/PNG/WEBP")

        # mock บัตร: ตรวจรูปแบบพอประมาณ (ไม่ต้องถูกต้อง 100%)
        if method == "credit_card":
            for f in ("cardholder_name", "card_number", "expiration", "cvv"):
                if not self.data.get(f):
                    self.add_error(None, "กรุณากรอกข้อมูลบัตรให้ครบเพื่อทดสอบการชำระเงินแบบ mock")

        return cleaned
