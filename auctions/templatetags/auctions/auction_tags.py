from django import template

from auctions.models import Auction

register = template.Library()


@register.inclusion_tag('auctions/watchlist.html')
def show_listings(filter=None):
    if filter:
        return Auction.objects.filter(category=filter)
    else:
        return Auction.objects.all()
