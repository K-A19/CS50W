from django.shortcuts import render, redirect
from django.urls import reverse
import re
import os.path
import random as r
from . import util


def index(request):

    # Displays the list of current entries
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):

    # Ensures the requested entry exists and shows an error otherwise
    if util.get_entry(title) == None:
        return render(request, "encyclopedia/error.html", {
            "error": f'The { title } entry requested does not exist'
        })

    # Creates a variable to store the entry requested
    entry = util.get_entry(title)

    # Displayes the entry with Markdown converted to HTML for the user
    return render(request, f"encyclopedia/entry.html", {
        "title": title,
        "content": util.convert(entry),
    })


def search(request):

    # Ensures the form is valid and otherwise redirects to the home page
    if request.method == 'GET' or not isinstance(request.POST.get('q'), str) :
        return redirect(reverse('index'))
    
    if request.POST.get('q').isspace():
        return render(request, "encyclopedia/error.html", {
            "error": "You cannot provide a search phrase with just spaces. Please try again"
        })
    
    # Creates variables to store all entries and the search phrase
    keyword = request.POST.get('q').strip()
    entries = util.list_entries()

    # Compares the search phrase to enries in lowercase and displays the entry page for the search phrase if it exists
    if keyword.lower() in [entry.lower() for entry in entries]:
        return redirect(reverse('entry', args=(keyword,)))
    
    # Creates a variable which stores all entries that the search phrase is a substring of
    superstring = []

    # Populates superstring list with all entries which the search phrase is a substring of
    for entry in util.list_entries():
        if re.search(keyword , entry, re.IGNORECASE) != None:
            superstring.append(entry)

    # Displays an error if there are no entries similar to that of the search phrase
    if len(superstring) < 1:
        return render(request, "encyclopedia/error.html", {
            "error": f"There are no search results similar to the search string '{keyword}'"
        })

    # Displays a page with all entries similar to that of the search phrase
    return render(request, "encyclopedia/search.html", {
        "entries": superstring
    })


def new(request):

    # Stores the inputed data from the form if it is submitted
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        entries = util.list_entries()

        # Displays an error if there is already an entry that exists with the same title
        if str(title).lower() in [entry.lower() for entry in entries]:
            return render(request, "encyclopedia/error.html", {
                "error": f"Sorry, there is already another entry with the name '{title}'"
            })

        # Saves the entry given it passes all the previous checks
        util.save_entry(title,content)

        # Displays the new entry's page
        return redirect(reverse('entry', args=(title,)))

    # Displays the form as the page was just moved to and the form hasn't been submitted
    return render(request, "encyclopedia/new.html")


def edit(request, title):

    # Stores the inputed data from the form if it is submitted
    if request.method == "POST":
        content = request.POST.get('content')

        # Saves edited version of the entry 
        util.save_entry(title,content)

        # Displays the new edited version of the entry
        return redirect(reverse('entry', args=(title,)))
    
    content = util.get_entry(title)
    i = 0
    while True:
        try:
            trial = content[i]
        except IndexError:
            break

        if str(content)[i].isspace() and str(content[i-1]).isspace():
            content = content[:i] + content[i+1:]
            i -= 1
        i += 1

    # Displays the regular edit page as an entry has not actually been changed yet
    return render(request, "encyclopedia/edit.html", {
        "title" : title,
        "content": content
        
    })

def random(request):
     
     # Stores a list of all current entries made
     entries = util.list_entries()

     # Choses a random entry in the list via chosing a random list index
     entry = entries[r.randint(0, len(entries) - 1)]

    # Displays the randomly chosen entry
     return redirect(reverse('entry', args=(entry,)))