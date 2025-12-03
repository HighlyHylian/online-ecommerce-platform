from django.test import TestCase, Client
from django.urls import reverse
from main.models import CustomUser, Product, Order, OrderItem, Review, Cart, CartItem

class ReviewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.buyer = CustomUser.objects.create_user(username="buyer", password="pass1234", role="buyer", banned=False)
        self.seller = CustomUser.objects.create_user(username="seller", password="pass1234", role="seller", banned=False)
        self.product = Product.objects.create(name="Board", price=100, description="Cool", seller=self.seller, is_approved=True)
        self.order = Order.objects.create(buyer=self.buyer, amountDue=100)
        self.order_item = OrderItem.objects.create(order=self.order, product=self.product, quantity=1, pricePurchased=100)
        self.cart = Cart.objects.create(buyer=self.buyer)
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)

    def test_buyer_can_leave_review_after_purchase(self):
        self.client.login(username="buyer", password="pass1234")
        response = self.client.post(reverse("leave_review", args=[self.product.product_id]), {"rating": 5, "comment": "Great!"})
        self.assertTrue(Review.objects.filter(product=self.product, user=self.buyer).exists())

    def test_buyer_cannot_review_without_purchase(self):
        new_product = Product.objects.create(name="NewBoard", price=120, description="New", seller=self.seller, is_approved=True)
        self.client.login(username="buyer", password="pass1234")
        response = self.client.post(reverse("leave_review", args=[new_product.product_id]), {"rating": 5, "comment": "Test"})
        self.assertFalse(Review.objects.filter(product=new_product, user=self.buyer).exists())

    def test_seller_cannot_review_own_product(self):
        self.client.login(username="seller", password="pass1234")
        response = self.client.post(reverse("leave_review", args=[self.product.product_id]), {"rating": 5, "comment": "Test"})
        self.assertFalse(Review.objects.filter(product=self.product, user=self.seller).exists())

    def test_cart_total_price_calculation(self):
        self.assertEqual(self.cart.total_price(), 100)

    def test_prevent_duplicate_review_by_same_user(self):
        Review.objects.create(product=self.product, user=self.buyer, rating=5, comment="Awesome")
        self.client.login(username="buyer", password="pass1234")
        self.client.post(reverse("leave_review", args=[self.product.product_id]), {"rating": 4, "comment": "Second"})
        self.assertEqual(Review.objects.filter(product=self.product, user=self.buyer).count(), 1)
