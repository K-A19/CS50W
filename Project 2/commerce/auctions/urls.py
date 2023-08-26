from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.new, name="new"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("watching/<int:id>", views.watching, name="watching" ),
    path("close/<int:id>", views.close_listing, name="close_listing"),
    path("comment/<int:id>", views.comment, name="comment")
]
