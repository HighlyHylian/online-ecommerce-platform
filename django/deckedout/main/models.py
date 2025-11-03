from django.db import models

from django.contrib.auth.models import AbstractUser

from django.conf import settings



class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    
    banned = models.BooleanField(default=True)

    def __str__(self):
        return self.username




class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    

class Order (models.Model):


    
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders_as_seller')

    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders_as_buyer') 

    products = models.ManyToManyField(Product, through='OrderItem')

    created_at = models.DateTimeField(auto_now_add=True)

    amountDue = models.DecimalField(max_digits=10, decimal_places=2)
 
    def __str__(self):
        return f"Order #{self.pk} by {self.buyer}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    product = models.ForeignKey('Product', on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    pricePurchased = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.pk}"
    


