from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import OrderForm, TrackOrderForm
from .models import Menu, Order
from .models import OrderItem, Extra, MenuItem


def home(request):
    today = timezone.localdate()
    upcoming_menus = Menu.objects.filter(date__gte=today).order_by("date")
    return render(request, "canteen/home.html", {"upcoming_menus": upcoming_menus})


def menu_detail(request, menu_date):
    menu = get_object_or_404(Menu, date=menu_date)
    return render(request, "canteen/menu_detail.html", {"menu": menu})


def order_create(request, menu_date):
    menu = get_object_or_404(Menu, date=menu_date)
    menu_items = menu.items.all()

    if request.method == "POST":
        form = OrderForm(request.POST, menu_items=menu_items)
        if form.is_valid():
            order = form.save(commit=False)
            order.menu = menu
            order.save()
            selected_items = form.cleaned_data["items"]
            order.items.set(selected_items)
            order.extras.set(form.cleaned_data["extras"])

            # handle per-item extras posted as extras_for_<item_id> = comma-separated extra ids
            for item in selected_items:
                qty = int(request.POST.get(f"quantity_{item.id}", "1"))
                order_item = OrderItem.objects.create(order=order, menu_item=item, quantity=qty)
                extras_for = request.POST.getlist(f"extras_for_{item.id}")
                if extras_for:
                    order_item.extras.set([int(e) for e in extras_for])
                order_item.save()
            # after order created, redirect to payment choice (online/offline)
            return redirect("canteen:payment_choice", tracking_code=order.tracking_code)
    else:
        form = OrderForm(menu_items=menu_items, initial={"menu_date": menu.date})

    return render(request, "canteen/order_form.html", {"form": form, "menu": menu})


def payment_choice(request, tracking_code):
    order = get_object_or_404(Order, tracking_code=tracking_code)
    if request.method == "POST":
        payment_method = request.POST.get("payment_method", "offline")
        return redirect(
            "canteen:payment_result",
            tracking_code=order.tracking_code,
            payment_method=payment_method,
        )
    return render(request, "canteen/payment_choice.html", {"order": order})


def payment_result(request, tracking_code, payment_method):
    order = get_object_or_404(Order, tracking_code=tracking_code)
    return render(
        request,
        "canteen/payment_result.html",
        {"order": order, "payment_method": payment_method},
    )


def order_confirm(request, tracking_code):
    order = get_object_or_404(Order, tracking_code=tracking_code)
    return render(request, "canteen/order_confirm.html", {"order": order})


def track_order(request):
    order = None
    if request.method == "POST":
        form = TrackOrderForm(request.POST)
        if form.is_valid():
            tracking_code = form.cleaned_data["tracking_code"]
            phone = form.cleaned_data["phone"]
            order = Order.objects.filter(tracking_code=tracking_code, phone=phone).first()
            if not order:
                messages.error(request, "سفارش با اطلاعات وارد شده پیدا نشد.")
    else:
        form = TrackOrderForm()

    return render(request, "canteen/track_order.html", {"form": form, "order": order})
