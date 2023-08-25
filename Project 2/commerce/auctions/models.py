from django.contrib.auth.models import AbstractUser
from django.db import models

from django.core.validators import MinValueValidator
from decimal import Decimal

class User(AbstractUser):
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return f"{self.username}"


class Listing(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=500)
    bid = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    image = models.URLField(blank=True)
    category = models.CharField(max_length=64, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    time = models.DateTimeField(auto_now_add=True)
    watchers= models.ManyToManyField(User, blank=True, related_name='watchlist')
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"


class Bid(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    value = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.value} by {self.owner} for {self.listing}"
    

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    content = models.CharField(max_length=200)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"By {self.owner} about {self.listing} at {self.time}"
