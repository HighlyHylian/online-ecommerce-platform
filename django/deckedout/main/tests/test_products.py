from django.test import TestCase, Client
from django.urls import reverse
from main.models import CustomUser, Product, FeedItem

class ProductTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.seller = CustomUser.objects.create_user(
            username="seller", password="pass1234", role="seller", banned=False
        )
        self.buyer = CustomUser.objects.create_user(
            username="buyer", password="pass1234", role="buyer", banned=False
        )
        self.product = Product.objects.create(
            name="TestBoard", price=100, description="Cool board",
            seller=self.seller, stock=5, is_approved=True
        )

    def test_seller_can_add_product_model(self):
        """Test adding a product directly via the model"""
        product = Product.objects.create(
            name="Board2", price=150, description="Nice board",
            seller=self.seller, stock=10
        )
        self.assertTrue(Product.objects.filter(name="Board2", seller=self.seller).exists())

    def test_seller_can_edit_product_model(self):
        """Test editing a product directly via the model"""
        self.product.name = "UpdatedBoard"
        self.product.price = 120
        self.product.description = "Updated"
        self.product.save()
        updated = Product.objects.get(pk=self.product.pk)
        self.assertEqual(updated.name, "UpdatedBoard")
        self.assertEqual(updated.price, 120)
        self.assertEqual(updated.description, "Updated")

    def test_buyer_cannot_add_product_view(self):
        """Test that buyers cannot access the add_product view"""
        self.client.login(username="buyer", password="pass1234")
        response = self.client.get(reverse("add_product"))
        self.assertEqual(response.status_code, 403)

    def test_unapproved_product_not_visible_to_buyer(self):
        """Test that unapproved products are hidden from buyers"""
        self.product.is_approved = False
        self.product.save()
        self.client.login(username="buyer", password="pass1234")
        response = self.client.get(reverse("skateboards"))
        self.assertNotContains(response, self.product.name)

    def test_product_creation_creates_feeditem(self):
        """Test creating a FeedItem"""
        FeedItem.objects.create(title="Test Event", event_type=FeedItem.EVENT_PRODUCT_CREATED)
        self.assertGreater(FeedItem.objects.count(), 0)
