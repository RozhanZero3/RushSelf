import random
import jdatetime

from django.db import models


def generate_tracking_code(length):
    """Generate a numeric tracking code of a given length."""
    return "".join(random.choices("0123456789", k=length))


def build_unique_tracking_code():
    # start with a random length between 5 and 12. If collision occurs,
    # increase the length by 1 each retry to reduce chance of further collisions.
    length = random.randint(5, 12)
    code = generate_tracking_code(length)
    while Order.objects.filter(tracking_code=code).exists():
        length = min(length + 1, 20)
        code = generate_tracking_code(length)
    return code


class MenuItem(models.Model):
    name = models.CharField(max_length=200, verbose_name="نام غذا")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    price = models.PositiveIntegerField(verbose_name="قیمت")
    is_vegetarian = models.BooleanField(default=False, verbose_name="گیاهی")
    category = models.CharField(max_length=120, blank=True, verbose_name="دسته‌بندی")

    class Meta:
        verbose_name = "غذای منو"
        verbose_name_plural = "غذاهای منو"

    def __str__(self):
        return self.name


class Extra(models.Model):
    name = models.CharField(max_length=200, verbose_name="نام مخلفات")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    price = models.PositiveIntegerField(default=0, verbose_name="قیمت")

    class Meta:
        verbose_name = "مخلفات"
        verbose_name_plural = "مخلفات"

    def __str__(self):
        return self.name


class Menu(models.Model):
    date = models.DateField(unique=True, verbose_name="تاریخ")
    items = models.ManyToManyField(MenuItem, blank=True, related_name="menus", verbose_name="آیتم‌های منو")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")

    class Meta:
        ordering = ["date"]
        verbose_name = "منوی روزانه"
        verbose_name_plural = "منوهای روزانه"

    def __str__(self):
        try:
            shamsi = jdatetime.date.fromgregorian(date=self.date)
            return f"منوی {shamsi.strftime('%Y/%m/%d')}"
        except Exception:
            return f"منوی {self.date}"


class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELED = "canceled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "در انتظار"),
        (STATUS_CONFIRMED, "تایید شده"),
        (STATUS_CANCELED, "لغو شده"),
    ]

    tracking_code = models.CharField(max_length=20, unique=True, editable=False, verbose_name="کد رهگیری")
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="orders", verbose_name="منو")
    items = models.ManyToManyField(MenuItem, verbose_name="غذاهای سفارش داده شده")
    extras = models.ManyToManyField(Extra, blank=True, related_name="orders", verbose_name="مخلفات")
    first_name = models.CharField(max_length=120, verbose_name="نام")
    last_name = models.CharField(max_length=120, verbose_name="نام خانوادگی")
    student_id = models.CharField(max_length=50, verbose_name="شماره دانشجویی")
    phone = models.CharField(max_length=20, blank=True, default="", verbose_name="شماره تماس")
    note = models.TextField(blank=True, verbose_name="یادداشت")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name="وضعیت سفارش")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ثبت سفارش")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = build_unique_tracking_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"سفارش {self.tracking_code} - {self.student_id}"


class OrderItem(models.Model):
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="order_items", verbose_name="سفارش مربوطه")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, verbose_name="آیتم")
    extras = models.ManyToManyField(Extra, blank=True, related_name="order_items", verbose_name="مخلفات")
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

    def __str__(self):
        return f"{self.menu_item.name} x{self.quantity} ({self.order.tracking_code})"
