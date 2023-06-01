from django.contrib import admin

from auctions.models import Auction, User, Category, Bid

admin.site.register(Auction)
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Bid)

