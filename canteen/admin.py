import jdatetime

from django.contrib import admin

from .models import Extra, Menu, MenuItem, Order
from .models import OrderItem


def shamsi_date(value):
    if not value:
        return ""
    try:
        return jdatetime.date.fromgregorian(date=value).strftime("%Y/%m/%d")
    except Exception:
        return value


def shamsi_datetime(value):
    if not value:
        return ""
    try:
        greg = value
        shamsi = jdatetime.datetime.fromgregorian(datetime=greg)
        return shamsi.strftime("%Y/%m/%d %H:%M")
    except Exception:
        return value


# Simplify admin: show essential fields, reduce clutter, and use horizontal for many-to-many only where useful
admin.site.site_header = "پنل مدیریت سلف"
admin.site.site_title = "مدیریت سلف"
admin.site.index_title = "پنل مدیریت"


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "price_display")
    search_fields = ("name",)

    def price_display(self, obj):
        try:
            return f"{obj.price:,} تومان"
        except Exception:
            return obj.price
    price_display.short_description = "قیمت"


@admin.register(Extra)
class ExtraAdmin(admin.ModelAdmin):
    list_display = ("name", "price_display")
    search_fields = ("name",)

    def price_display(self, obj):
        try:
            return f"{obj.price:,} تومان"
        except Exception:
            return obj.price
    price_display.short_description = "قیمت"


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("shamsi_date", "created_at_shamsi")
    filter_horizontal = ("items",)
    search_fields = ("date",)

    def shamsi_date(self, obj):
        return shamsi_date(obj.date)
    shamsi_date.short_description = "تاریخ"

    def created_at_shamsi(self, obj):
        return shamsi_datetime(obj.created_at)
    created_at_shamsi.short_description = "زمان ایجاد"
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("menu_item", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # keep the admin succinct: tracking, student id, phone, status, and menu date
    list_display = ("tracking_code", "student_id", "phone", "menu_shamsi", "status")
    list_filter = ("status",)
    search_fields = ("student_id", "tracking_code", "phone")
    raw_id_fields = ("menu",)
    inlines = [OrderItemInline]

    def menu_shamsi(self, obj):
        return shamsi_date(obj.menu.date)
    menu_shamsi.short_description = "تاریخ منو"

    class Media:
        css = {
            'all': ('canteen/admin-custom.css',)
        }
