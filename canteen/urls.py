from django.urls import path

from . import views

app_name = "canteen"

urlpatterns = [
    path("", views.home, name="home"),
    path("menu/<str:menu_date>/", views.menu_detail, name="menu_detail"),
    path("order/<str:menu_date>/", views.order_create, name="order_create"),
    path("payment/<str:tracking_code>/", views.payment_choice, name="payment_choice"),
    path("payment/<str:tracking_code>/<str:payment_method>/", views.payment_result, name="payment_result"),
    path("order/confirm/<str:tracking_code>/", views.order_confirm, name="order_confirm"),
    path("track/", views.track_order, name="track_order"),
]
