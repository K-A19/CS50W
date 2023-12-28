from django.contrib import admin
from .models import User, Post

# Register the user model
class UserAdmin(admin.ModelAdmin):
    list_display= ("id", "username")

admin.site.register(User, UserAdmin)


# Register the post model
class PostAdmin(admin.ModelAdmin):
    list_display= ("id", "owner", "content", "timestamp", "likes")

admin.site.register(Post, PostAdmin)
