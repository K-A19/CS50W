from django.contrib import admin
from .models import User, Listing, Bid, Comment

# Registers the User model
class UserAdmin(admin.ModelAdmin):
    list_display= ("id", "username")

admin.site.register(User, UserAdmin)

# Registers the Listing model
class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "bid", "image", "category", "owner", "time", "active","winner")

admin.site.register(Listing, ListingAdmin)

# Registers the Bid model
class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "listing", "value", "time")

admin.site.register(Bid, BidAdmin)

# Registers the Comment model
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "listing", "content", "time")

admin.site.register(Comment, CommentAdmin)