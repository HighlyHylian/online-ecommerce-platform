from django.contrib import admin
from .models import FeedItem

@admin.register(FeedItem)
class FeedItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'pub_date')
    list_filter = ('event_type',)
    search_fields = ('title', 'description')