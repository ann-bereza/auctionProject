from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listings/<int:auction_id>", views.get_auction, name="listings"),
    path("create", views.create_auction, name="create"),
    path("categories", views.get_categories, name="categories"),
    path("categories/<int:cat_id>", views.get_listings_by_category, name="category"),
    path("bid", views.bid, name="bid"),
    path("listings/<int:auction_id>/close", views.close_auction, name="close"),
    path("listings/<int:auction_id>/watchlist/add", views.add_to_watchlist, name="watchlist_add"),
    path("listings/<int:auction_id>/watchlist/remove", views.remove_from_watchlist, name="watchlist_remove"),
    path("watchlist", views.get_watchlist, name="watchlist_get"),
]