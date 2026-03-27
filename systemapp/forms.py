from django import forms

from django.contrib.auth.forms import PasswordChangeForm

from .models import AdminSettings, Cattle, Farm, worker_login


class WorkerRegistryForm(forms.ModelForm):
    class Meta:
        model = worker_login
        fields = ["photo", "full_name", "phone_number", "preferred_language", "is_active"]
        widgets = {
            "photo": forms.ClearableFileInput(attrs={"accept": "image/*", "class": "hidden", "id": "id_photo"}),
            "full_name": forms.TextInput(
                attrs={
                    "placeholder": "Enter full name",
                    "class": "w-full border-2 border-gray-300 focus:border-primary rounded-xl px-4 py-3 outline-none",
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "placeholder": "+91 98765 43210",
                    "class": "w-full border-2 border-gray-300 focus:border-primary rounded-xl px-4 py-3 outline-none",
                }
            ),
            "preferred_language": forms.Select(
                attrs={
                    "class": "w-full border-2 border-gray-300 focus:border-primary rounded-xl px-4 py-3 outline-none",
                }
            ),
            "is_active": forms.HiddenInput(),
        }

    def clean_full_name(self):
        return " ".join((self.cleaned_data.get("full_name") or "").split())

    def clean_phone_number(self):
        return (self.cleaned_data.get("phone_number") or "").strip()


class AdminCattleAddForm(forms.ModelForm):
    class Meta:
        model = Cattle
        fields = [
            "farm",
            "tag_id",
            "tag_number",
            "name",
            "cattle_type",
            "breed",
            "age_months",
            "health_status",
            "is_for_sale",
            "price",
            "image",
            "purchased_from_name",
            "purchased_from_contact",
            "purchased_from_location",
            "purchased_from_address",
            "purchase_notes",
        ]
        widgets = {
            "farm": forms.Select(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none"}),
            "tag_id": forms.TextInput(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none", "placeholder": "Unique Tag ID (e.g., GV-009)"}),
            "tag_number": forms.TextInput(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none", "placeholder": "Optional tag number"}),
            "name": forms.TextInput(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none", "placeholder": "Optional cattle name"}),
            "cattle_type": forms.Select(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none"}),
            "breed": forms.TextInput(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none", "placeholder": "Breed (e.g., Jersey)"}),
            "age_months": forms.NumberInput(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none", "min": "0", "placeholder": "Age in months"}),
            "health_status": forms.Select(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none"}),
            "price": forms.NumberInput(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none", "step": "0.01", "placeholder": "Price (optional)"}),
            "image": forms.ClearableFileInput(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none", "accept": "image/*"}),
            "purchased_from_name": forms.TextInput(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none", "placeholder": "Seller / Market / Vendor name"}),
            "purchased_from_contact": forms.TextInput(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none", "placeholder": "Phone / email (optional)"}),
            "purchased_from_location": forms.TextInput(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none", "placeholder": "City, State"}),
            "purchased_from_address": forms.Textarea(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none", "rows": 3, "placeholder": "Full address (optional)"}),
            "purchase_notes": forms.Textarea(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none", "rows": 3, "placeholder": "Notes (invoice no, auction, etc.)"}),
        }

    def clean_tag_id(self):
        tag_id = (self.cleaned_data.get("tag_id") or "").strip()
        if not tag_id:
            raise forms.ValidationError("Tag ID is required.")
        return tag_id

    def clean_age_months(self):
        age_months = self.cleaned_data.get("age_months")
        if age_months is None:
            return 0
        if age_months < 0:
            raise forms.ValidationError("Age cannot be negative.")
        return age_months

    def clean(self):
        cleaned = super().clean()
        is_for_sale = cleaned.get("is_for_sale")
        price = cleaned.get("price")
        if is_for_sale and not price:
            self.add_error("price", "Price is required when marking cattle for sale.")
        return cleaned


class AdminSettingsForm(forms.ModelForm):
    class Meta:
        model = AdminSettings
        fields = [
            "payee_name",
            "upi_id",
            "currency",
            "bank_name",
            "bank_account_number",
            "bank_ifsc",
            "support_email",
            "support_phone",
        ]
        widgets = {
            "payee_name": forms.TextInput(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none"}),
            "upi_id": forms.TextInput(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none"}),
            "currency": forms.TextInput(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none", "placeholder": "INR"}),
            "bank_name": forms.TextInput(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none"}),
            "bank_account_number": forms.TextInput(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none"}),
            "bank_ifsc": forms.TextInput(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none"}),
            "support_email": forms.EmailInput(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none"}),
            "support_phone": forms.TextInput(attrs={"class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none"}),
        }


class AdminPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update(
                {
                    "class": "w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-primary outline-none",
                }
            )
