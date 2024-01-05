from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator

from .models import User, Post


def index(request, following=None):

    if following == "following":

        # Makes the title of the page following
        title = "Following"

        # Gets all posts which have been made by users which the user follow
        posts= Post.objects.filter(owner__in=User.objects.filter(followers=request.user)).order_by('-timestamp')
    else:

        # Makes the title of the page all posts
        title = "All Posts"

        # Gets all the posts which have been made
        posts = Post.objects.all().order_by('-timestamp')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "title" : title,
        "page_obj" : page_obj,
    })


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required(login_url='login')
def new_post(request):
    
    # Ensures a form was filled first to create the post
    if request.method == 'POST':
         
         # Gets information required to create a new post
         content = request.POST.get('content')
         user = request.user 
         
         # Creates and saves the new post as an object in the Posts model
         post = Post.objects.create(owner=user, content=content)
         post.save

    # Redirects the user beck to the main page
    return HttpResponseRedirect(reverse('index'))


def profile(request, id):

    # Gets the ids of all existing users
    ids = [x[0] for x in User.objects.all().values_list('id')]
 
    # Ensures the user is already existent
    if id not in ids:
        return render(request, "network/profile.html", {
        "viewing" : None,
        "message" : f"The user with id {id} does not exit",
        "posts" : None,
        })

    # If the user exists, their information is gotten
    viewing = User.objects.get(id=id)

    # Checks if the follow/unfollow button has been clicked
    if request.method == "POST":

        # Gets the user making the request
        user = User.objects.get(id=request.POST["User"])

        # Ensures the user making the request is not the same as the user they want to follow/unfollow
        if user != viewing:

            # Gets the actions to be performed
            action = request.POST["Action"]

            # Carries out the following of a user if the actions was to follow
            if action == "Follow":
                viewing.followers.add(user)
                user.following.add(viewing)
                viewing.save()
                user.save()

            # Carries out the unfollowing of a user if the actions was to unfollow
            elif action == "Unfollow":
                viewing.followers.remove(user)
                user.following.remove(viewing)
                viewing.save()
                user.save()

    # Gets all the posts the searched user is an author of
    posts = Post.objects.filter(owner = viewing)

    # Implements pagination by 10 posts
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    print(page_obj)

    # If the current user already follows the viewed user, 1 is returned, otherwise None is returned
    followers_list = User.objects.filter(following=viewing)
    followed = 1 if request.user in followers_list else None

    # Counts the number of people who follow the user and people the user is following
    followers = viewing.followers.count()
    following = viewing.following.count()

    # Displays the user's profile page
    return render(request, "network/profile.html", {
        "viewing" : viewing,
        "message" : None,
        "page_obj" : page_obj,
        "followers" : followers,
        "following" : following,
        "followed" : followed,
    })