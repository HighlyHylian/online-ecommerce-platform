from django.db import models

from django.contrib.auth.models import AbstractUser

from django.conf import settings





class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')

    def __str__(self):
        return self.username



class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
        # Helper method to calculate average rating
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return round(sum(r.rating for r in reviews) / reviews.count(), 1)

    # Helper method to get review count
    def review_count(self):
        return self.reviews.count()
    

class Order(models.Model):
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders_as_buyer'
    )
    products = models.ManyToManyField('Product', through='OrderItem')
    created_at = models.DateTimeField(auto_now_add=True)
    amountDue = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order #{self.pk} by {self.buyer.username}"

    

# models.py

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    pricePurchased = models.DecimalField(max_digits=10, decimal_places=2)

    # NEW FIELD
    refund_status = models.CharField(
        max_length=20,
        choices=[
            ('none', 'No Refund'),
            ('requested', 'Requested'),
            ('approved', 'Approved'),
            ('denied', 'Denied'),
        ],
        default='none'
    )

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.pk}"

    def subtotal(self):
        return self.pricePurchased * self.quantity



class SellerBalance(models.Model):
    seller = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='balance'
    )
    site_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.seller.username}'s Balance: ${self.site_balance}"


'''class RefundRequest(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField()
    is_approved = models.BooleanField(null=True, blank=True)  # None = pending
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refund Request for {self.order_item.product.name} by {self.buyer.username}"'''

from django.db import models
from django.conf import settings

class RefundRequest(models.Model):
    order_item = models.ForeignKey('OrderItem', on_delete=models.CASCADE)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('requested', 'Requested'), ('approved', 'Approved'), ('denied', 'Denied')],
        default='requested'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refund for {self.order_item.product.name} ({self.status})"




class Cart(models.Model):
    buyer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.buyer.username}"

    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def subtotal(self):
        return self.quantity * self.product.price


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.rating} stars"
