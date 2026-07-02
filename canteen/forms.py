from django import forms
from django.utils import timezone

from .models import Extra, MenuItem, Order
from .models import OrderItem


class OrderForm(forms.ModelForm):
    menu_date = forms.DateField(widget=forms.HiddenInput())
    items = forms.ModelMultipleChoiceField(
        queryset=MenuItem.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="غذاهای انتخابی",
    )
    # top-level extras field kept for backward compatibility; per-item extras handled in templates
    extras = forms.ModelMultipleChoiceField(
        queryset=Extra.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="مخلفات عمومی",
    )

    class Meta:
        model = Order
        fields = [
            "first_name",
            "last_name",
            "student_id",
            "phone",
            "menu_date",
            "items",
            "extras",
            "note",
        ]
        labels = {
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "student_id": "شماره دانشجویی",
            "phone": "شماره تماس",
            "note": "توضیحات اضافی",
        }
        widgets = {
            "note": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, menu_items=None, **kwargs):
        super().__init__(*args, **kwargs)
        if menu_items is not None:
            self.fields["items"].queryset = menu_items
        self.fields["items"].help_text = "حداقل یک غذا انتخاب کنید."
        self.fields["extras"].queryset = Extra.objects.all()
        self.fields["extras"].help_text = "در صورت تمایل می‌توانید مخلفات را انتخاب کنید."

        # remove email if present in model/form (ensures email is not shown anywhere)
        if "email" in self.fields:
            del self.fields["email"]

        # placeholder to receive per-item extras selections via POST; not rendered by Django form fields
        self.per_item_extras = {}

    def clean_menu_date(self):
        menu_date = self.cleaned_data["menu_date"]
        min_date = timezone.localdate() + timezone.timedelta(days=2)
        if menu_date < min_date:
            raise forms.ValidationError(
                "سفارش باید حداقل دو روز قبل از تاریخ سرو ثبت شود."
            )
        return menu_date


class TrackOrderForm(forms.Form):
    tracking_code = forms.CharField(label="کد رهگیری")
    phone = forms.CharField(label="شماره تماس")
