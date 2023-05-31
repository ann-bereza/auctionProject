from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import CreateAuction, CreateBid
from .models import User, Auction, Category, Bid, Watchlist


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def index(request):
    return render(request, "auctions/index.html", {
        'auctions': Auction.objects.all()
    })


def get_auction(request, auction_id):
    auction = Auction.objects.get(id=auction_id)
    is_owner = request.user == auction.owner
    is_winner = request.user == auction.winner
    bid = Bid(auction=auction)
    bid_form = CreateBid(instance=bid)
    latest_auction_bid = bid.get_latest_auction_bid(auction)
    is_auth = False
    in_watchlist = False
    if request.user.is_authenticated:
        is_auth = True
        watchlist = Watchlist.objects.filter(user=request.user)
        if watchlist:
            w = watchlist[0]
            auctions = w.item.all()
            in_watchlist = auction in auctions
    return render(request, "auctions/auction.html", {
        "auction": auction, "owner": is_owner, "winner": is_winner, "bid": bid_form, "latest_bid": latest_auction_bid,
        "auction_id": auction_id, "in_watchlist": in_watchlist, "is_auth": is_auth
    })


def get_categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def get_listings_by_category(request, cat_id):
    auctions = Auction.objects.filter(category=cat_id)
    active_auctions = []
    for a in auctions:
        if a.isActive:
            active_auctions.append(a)
    return render(request, "auctions/index.html", {
        "auctions": active_auctions
    })


def create_auction(request):
    form = CreateAuction(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            instance = form.save(commit=False)
            instance.owner = request.user
            instance.save()
            return redirect('index', )

    return render(request, "auctions/create_auction.html", {'form': form})


def bid(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Not valid")
    bid_form = CreateBid(request.POST)
    if bid_form.is_valid():
        instance = bid_form.save(commit=False)
        auction = instance.auction
        if instance.amount > auction.price and (
                auction.currentBid is None or instance.amount > auction.currentBid.amount):
            instance.user = request.user
            instance.save()
            auction.currentBid = instance
            auction.save()
            watchlist, _ = Watchlist.objects.get_or_create(user=request.user)
            if auction not in watchlist.item.all():
                watchlist.item.add(auction)
                messages.success(request, "You've successfully added a new bid.")
                messages.success(request, "Auction added to your watchlist")
            return HttpResponseRedirect(reverse('listings', args=(instance.auction_id,)))
        else:
            messages.error(
                request, f'Bid is less than the latest and/or starting bid: {auction.currentBid.amount}')
            return HttpResponseRedirect(reverse('listings', args=(instance.auction_id,)))


@login_required(login_url='/login')
def close_auction(request, auction_id):
    auction = Auction.objects.filter(pk=auction_id)[0]
    if auction.currentBid:
        winner = User.objects.filter(pk=auction.currentBid.user_id)[0]
        auction.winner = winner
    auction.isActive = False
    auction.save()
    messages.info(
        request, f'Auction {auction} is closed successfully!')
    return redirect('index', )


def get_watchlist(request):
    try:
        watchlist = Watchlist.objects.filter(user=request.user)[0]
        auctions = watchlist.item.all()
        return render(request, "auctions/watchlist.html", context={
            "auctions": auctions, "watchlist": watchlist
        })
    except IndexError:
        return render(request, "auctions/watchlist.html")


def add_to_watchlist(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    watchlist, _ = Watchlist.objects.get_or_create(user=request.user)
    if watchlist.item.contains(auction):
        messages.add_message(request, messages.SUCCESS, "This auction is already in your watchlist")
        return HttpResponseRedirect(reverse('listings', args=(auction_id,)))
    else:
        watchlist.item.add(auction)
        messages.add_message(request, messages.SUCCESS, "Auction added to your watchlist")
        return HttpResponseRedirect(reverse('listings', args=(auction_id,)))


def remove_from_watchlist(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    watchlist = Watchlist.objects.get(user=request.user)
    items = watchlist.item.all()
    if auction in items:
        watchlist.item.remove(auction)
        messages.add_message(request, messages.SUCCESS, "This auction was removed from your watchlist successfully")
        return HttpResponseRedirect(reverse('listings', args=(auction_id,)))
    messages.add_message(request, messages.SUCCESS, "Successfully added to your watchlist")
    return HttpResponseRedirect(reverse('listings', args=(auction_id,)))
