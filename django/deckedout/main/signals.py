# new file
from django.contrib.auth import get_user_model
from django.contrib.admin.models import LogEntry
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import FeedItem, Product  # Product expected in main.models

User = get_user_model()

@receiver(post_save, sender=User)
def on_user_created(sender, instance, created, **kwargs):
    if created:
        FeedItem.objects.create(
            title=f"New user: {instance.get_username()}",
            description=f"User {instance.get_username()} was created.",
            pub_date=timezone.now(),
            event_type=FeedItem.EVENT_USER_CREATED,
        )

@receiver(post_save, sender=Product)
def on_product_created(sender, instance, created, **kwargs):
    if created:
        FeedItem.objects.create(
            title=f"New product: {getattr(instance, 'name', instance.pk)}",
            description=f"Product created by seller: {getattr(instance, 'seller', 'unknown')}",
            pub_date=timezone.now(),
            event_type=FeedItem.EVENT_PRODUCT_CREATED,
        )

@receiver(post_save, sender=LogEntry)
def on_admin_action(sender, instance, created, **kwargs):
    if created:
        FeedItem.objects.create(
            title=f"Admin: {instance.get_action_flag_display()} on {instance.content_type}",
            description=f"User {instance.user} performed admin action {instance.get_action_flag_display()} on {instance.object_repr}",
            pub_date=timezone.now(),
            event_type=FeedItem.EVENT_ADMIN_ACTION,
        )