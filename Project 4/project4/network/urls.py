
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post, name="new_post"),
    path("profile/<int:id>", views.profile, name="profile"),
    path("<str:following>", views.index, name="following"),
    path("post/<int:post_id>", views.post, name="post")
]
