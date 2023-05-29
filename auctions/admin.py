from django.contrib import admin

from auctions.models import Auction, User, Category

admin.site.register(Auction)
admin.site.register(User)
admin.site.register(Category)

