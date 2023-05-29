from django import forms
from django.forms import ModelForm

from .models import Auction, Bid


class CreateAuction(ModelForm):
    class Meta:
        model = Auction
        fields = ["title", "description", "imageURL", "category", "price", ]

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "imageURL": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"})
        }


class CreateBid(ModelForm):
    class Meta:
        model = Bid
        fields = ["auction", "amount"]

        widgets = {
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
            "auction": forms.HiddenInput()
        }