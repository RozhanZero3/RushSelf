from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Menu, MenuItem


class HomeViewTests(TestCase):
    def test_homepage_shows_upcoming_menu_items(self):
        item = MenuItem.objects.create(name="کباب کوبیده", price=25000)
        menu = Menu.objects.create(date=timezone.localdate() + timezone.timedelta(days=3))
        menu.items.add(item)

        response = self.client.get(reverse("canteen:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "کباب کوبیده")
        self.assertContains(response, reverse("canteen:order_create", kwargs={"menu_date": menu.date.strftime("%Y-%m-%d")}))

    def test_homepage_hides_past_menus(self):
        past_menu = Menu.objects.create(date=timezone.localdate() - timezone.timedelta(days=1))
        response = self.client.get(reverse("canteen:home"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, past_menu.date.strftime("%Y-%m-%d"))
