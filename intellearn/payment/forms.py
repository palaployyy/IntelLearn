from django import forms
from .models import Payment

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

class PaymentForm(forms.ModelForm):
    # ฟิลด์ mock บัตร (ไม่บันทึก DB)
    cardholder_name = forms.CharField(required=False, label="Cardholder Name")
    card_number     = forms.CharField(required=False, label="Card Number")
    expiration      = forms.CharField(required=False, label="Expiration Date (MM/YY)")
    cvv             = forms.CharField(required=False, label="CVV")

    class Meta:
        model = Payment
        fields = ["method", "proof"]
        widgets = {"method": forms.RadioSelect(choices=Payment.Method.choices)}

    def clean(self):
        cleaned = super().clean()
        method = cleaned.get("method")
        proof  = cleaned.get("proof")

        # ถ้าเป็นโอน/PromptPay ต้องแนบสลิป
        if method in (Payment.Method.TRANSFER, Payment.Method.PROMPTPAY):
            if not proof:
                self.add_error("proof", "กรุณาอัปโหลดสลิปเพื่อยืนยันการชำระเงิน")
            if proof:
                if proof.size > 5 * 1024 * 1024:
                    self.add_error("proof", "ไฟล์ต้องไม่เกิน 5MB")
                if getattr(proof, "content_type", "") not in ALLOWED_IMAGE_TYPES:
                    self.add_error("proof", "รองรับเฉพาะ JPG/PNG/WEBP")

        # mock บัตร: บังคับกรอกครบ
        if method == Payment.Method.CREDIT_CARD:
            required = ["cardholder_name", "card_number", "expiration", "cvv"]
            for f in required:
                if not self.data.get(f):
                    self.add_error(None, "กรุณากรอกข้อมูลบัตรให้ครบ (โหมด mock)")

        return cleaned
