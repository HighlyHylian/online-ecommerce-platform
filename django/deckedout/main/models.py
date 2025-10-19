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
    is_approved = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)

    def __str__(self):
        return self.name

