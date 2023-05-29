from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}".capitalize()

    @property
    def get_products(self):
        return Auction.objects.filter(category=self.name)

    def get_absolute_url(self):
        return reverse("category", kwargs={"cat_id": self.pk})


class Auction(models.Model):
    category = models.ForeignKey(
        'Category',
        related_name="auctions_category",
        on_delete=models.PROTECT
    )
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=2048)
    imageURL = models.URLField(max_length=500, default='')
    price = models.IntegerField()
    isActive = models.BooleanField(default=True)
    owner = models.ForeignKey("User", on_delete=models.PROTECT)
    currentBid = models.ForeignKey("Bid", on_delete=models.PROTECT, related_name="auction_current_bid", null=True)
    winner = models.ForeignKey("User", on_delete=models.PROTECT, related_name="auction_winner", null=True)

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse("listings", kwargs={"auction_id": self.pk})


class User(AbstractUser):

    def __str__(self):
        return f"{self.username}"


class Bid(models.Model):
    amount = models.FloatField(max_length=12)
    auction = models.ForeignKey('Auction',
                                on_delete=models.PROTECT)
    user = models.ForeignKey('User',
                             related_name="user_bid",
                             on_delete=models.PROTECT)

    def get_latest_auction_bid(self, auction):
        if auction.currentBid is None:
            return None
        return Bid.objects.filter(auction=auction).order_by('-id')[0]

    def __str__(self):
        return f'({self.amount})'

    def get_bid_user(self, auction):
        instance = Bid.objects.filter(user=auction)
        pass


class Watchlist(models.Model):
    user = models.ForeignKey('User', on_delete=models.PROTECT)
    item = models.ManyToManyField(Auction)

    def __str__(self):
        return f"{self.user}'s WatchList"
