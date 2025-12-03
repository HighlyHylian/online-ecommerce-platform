from django.test import TestCase, Client
from django.urls import reverse
from main.models import CustomUser

class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.buyer = CustomUser.objects.create_user(username="buyer1", password="pass1234", role="buyer", banned=False)
        self.seller = CustomUser.objects.create_user(username="seller1", password="pass1234", role="seller", banned=False)
        self.banned_user = CustomUser.objects.create_user(username="banned", password="pass1234", role="buyer", banned=True)

    def test_buyer_can_login(self):
        response = self.client.post(reverse("login"), {"username": "buyer1", "password": "pass1234"})
        self.assertEqual(response.status_code, 302)  # redirect on success

    def test_seller_can_login(self):
        response = self.client.post(reverse("login"), {"username": "seller1", "password": "pass1234"})
        self.assertEqual(response.status_code, 302)

    def test_banned_user_cannot_login(self):
        response = self.client.post(reverse("login"), {"username": "banned", "password": "pass1234"})
        self.assertContains(response, "Your account is banned")

    def test_signup_creates_buyer(self):
        response = self.client.post(reverse("signup"), {
            "username": "newbuyer",
            "password1": "newpass123",
            "password2": "newpass123",
            "role": "buyer"
        })
        self.assertTrue(CustomUser.objects.filter(username="newbuyer", role="buyer").exists())

    def test_signup_creates_seller(self):
        response = self.client.post(reverse("signup"), {
            "username": "newseller",
            "password1": "newpass123",
            "password2": "newpass123",
            "role": "seller"
        })
        self.assertTrue(CustomUser.objects.filter(username="newseller", role="seller").exists())
