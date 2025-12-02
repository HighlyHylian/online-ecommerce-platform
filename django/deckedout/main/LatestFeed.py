# new file
from django.contrib.syndication.views import Feed
from django.urls import reverse

from .models import FeedItem

class LatestFeed(Feed):
    title = "Site activity feed"
    link = "/"
    description = "Recent users, products, and admin actions."

    def items(self):
        return FeedItem.objects.all()[:50]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return item.link or '/'

    def item_pubdate(self, item):
        return item.pub_date