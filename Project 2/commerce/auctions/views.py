from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Bid, Comment
from .forms import NewListingForm, NewBidForm



def index(request):
    # Gets all the listings which are currenctly active
    listings = Listing.objects.filter(active=True)

    # Gets all the currently made bids
    bidings = Bid.objects.all()
    bids = {}

    # Sets the current price to the minimum bid set by the owner first
    for listing in listings:
        bids[listing.title] = listing.bid

    # Updates the current bid to the max bid that has been made
    for bid in bidings:
        if bid.listing in listings:
            if bid.value > bids[bid.listing.title]:
                bids[bid.listing.title] = bid.value

    watchlist= None
    if request.user.is_authenticated:
        watchlist = request.user.watchlist.all()

    return render(request, "auctions/index.html", {
        "listings" : listings,
        "bids" : bids,
        "user" : request.user,
        "watchlist": watchlist,
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


@login_required(login_url='login')
def new(request): 
    
    # Checks whether a form was submitted or not 
    if request.method == 'POST':
        
        # Creates a form instance and populate it with data from the request
        form = NewListingForm(request.POST)

        # Checks whether all for data is valid
        if form.is_valid():

            listing = Listing.objects.create(title=form.cleaned_data['title'], description=form.cleaned_data['description'], bid=form.cleaned_data['bid'], image=form.cleaned_data['image'], category=form.cleaned_data['category'], owner=User.objects.get(id=request.user.id))

            # Redirect to the active listing page
            return HttpResponseRedirect(reverse("index"))

    # A form wasn't submitted so the form will be displayed for the user to submit
    return render(request, 'auctions/new.html', {'form': NewListingForm()})


@login_required(login_url='login')
def listing(request, id):

    # Gets the information on a listing by its id number
    listing = Listing.objects.get(id=id)

    # Gets all the bids made for this listing
    bids = Bid.objects.filter(listing=listing)

    # Creates a varaible to store any error messages
    message = None
    
    # Sets the current price to the minimum bid set by the owner first
    price = listing.bid

    # Updates the current bid to the max bid that has been made
    for bid in bids:
        if bid.value > price:
            price = bid.value

    # Gets the total number of bids currently made for the listing
    bid_num = len(bids)

    # Determines if the current listing is in the current user's watchlist
    if listing in request.user.watchlist.all():
        watchlisted = True
    else:
        watchlisted = False

    # Gets all the comments for the listing
    comments = Comment.objects.filter(listing=listing)

    if request.method == "POST":

        # Creates a new form instance and populates it with the submitted dataset
        form = NewBidForm(request.POST)

        if form.is_valid():
            # Gets the form data after it has been validated
            bid = form.cleaned_data['bid']

        if bid >= listing.bid and bid > price:
            # Creates a new bid if the user made bid is large enough
            new_bid = Bid.objects.create(owner=request.user, listing=listing, value=bid)

            # Updates previously calculated values about the bids of the current listing
            price = new_bid.value
            bid_num += 1

        else:
            # Displays an error for the user if their bid is less than the minimum bid possible        
            if bid <= price:
                message = 'The proposed bid has to be greater than the maximum bid currently made'

            # Displays an error for the user if their bid is less than the maximum bid currently made
            if bid < listing.bid:
                message = 'The proposed bid has to be greater than the minimum bid set by the owner'

    return render(request, 'auctions/listing.html', {'listing': listing, 'price': price, 'user': request.user, 'form': NewBidForm(), 'bid_num': bid_num, 'message': message, 'watchlisted': watchlisted, 'comments': comments})


@login_required(login_url='login')
def watching(request, id):
    if request.method == 'POST':
        # Gets the action to be performed and the listing on which it shall be performed on
        listing = Listing.objects.get(id=id)
        action = request.POST.get('Watchlist')

        # Adds the listing to the current user's watchlist
        if action == 'Add To Watchlist':
            listing.watchers.add(request.user)

        # Removes the listing from the current user's watchlist
        elif action == 'Remove From Watchlist':
            listing.watchers.remove(request.user)

    return HttpResponseRedirect(reverse("listing", args=(id,)))


@login_required(login_url='login')
def close_listing(request, id):
    if request.method == 'POST':
        # Gets the action to be performed and the listing on which it shall be performed on
        listing = Listing.objects.get(id=id)
        action = request.POST.get('Close')

        # Ensures the action is actually to close the listing
        if action == 'Close Listing':

            # Sets the listing as now closed/inactive
            listing.active = False

            try: 
                # Finds the user who made the maximum bid on the current listing
                winner = Bid.objects.filter(listing=listing).order_by('-value')[0].owner

                # Sets the user who had the maximum bid as the winner
                listing.winner = winner

            except Exception:

                winner = None
            
            # Gets all the users which have the listing on their watchlist
            users = User.objects.filter(watchlist__in = [listing])

            # Removes the listing from each user's watchlist
            for user in users:
                listing.watchers.remove(user)

            # Saves the listing an dupdates its fields
            listing.save()

    # Redirects the user to the home page
    return HttpResponseRedirect(reverse("index"))


@login_required(login_url='login')
def comment(request,id):
    if request.method == 'POST':
        
        # Gets the listing and action to be performed as well as the content of the possible content
        listing = Listing.objects.get(id=id)
        action = request.POST.get('Submit')
        content = request.POST.get('content')

        # Make sure the right action s performed
        if action == 'Make Comment':

            # Makes a new comment object in the comment model
            comment = Comment.objects.create(owner=request.user, listing=listing, content=content)

    # Redirects the user to the original listing page they were on
    return HttpResponseRedirect(reverse("listing", args=(id,)))


@login_required(login_url='login')
def watchlist(request):

    # Gets all the listings on the current user's watchlist
    watchlist = request.user.watchlist.all()

    # Gets all the currently made bids
    bidings = Bid.objects.all()
    bids = {}

    # Sets the current price to the minimum bid set by the owner first
    for listing in watchlist:
        bids[listing.title] = listing.bid

    # Updates the current bid to the max bid that has been made
    for bid in bidings:
        if bid.listing in watchlist:
            if bid.value > bids[bid.listing.title]:
                bids[bid.listing.title] = bid.value

    return render(request, "auctions/watchlist.html", {
        "bids" : bids,
        "user" : request.user,
        "watchlist": watchlist,
    })


def categories(request):
    # Gets all the active listings which also have a category
    active_categories = Listing.objects.filter(active=True).exclude(category='')

    # Creates a list to store all the active categories
    categories = []

    # Populates a list of all active categories
    for listing in active_categories:

        # Checks if the current listing category already exists in the list of categories
        if listing.category not in categories:

            # Adds the listing to the list of listings in that category
            categories.append(listing.category)

    print(categories)

    return render(request, "auctions/categories.html", {"categories" : categories})


def category(request, category):

    # Gets all of the active listings that are a part of this category
    listings = Listing.objects.filter(active=True, category=category)

    # Gets all the currently made bids
    bidings = Bid.objects.all()
    bids = {}

    # Sets the current price to the minimum bid set by the owner first
    for listing in listings:
        bids[listing.title] = listing.bid

    # Updates the current bid to the max bid that has been made
    for bid in bidings:
        if bid.listing in listings:
            if bid.value > bids[bid.listing.title]:
                bids[bid.listing.title] = bid.value

    watchlist= None
    if request.user.is_authenticated:
        watchlist = request.user.watchlist.all()

    return render(request, "auctions/category.html", {
        "category":category, 
        "listings":listings,
        "bids" : bids,
        "user" : request.user,
        "watchlist": watchlist,
        })