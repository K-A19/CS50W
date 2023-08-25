import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None

def convert(entry):
    """
    This converts the Markdown language used to write entries
    into HTML as to display each entry's page as intended.
    """

    # Makes a copy of the Markdown language used to make the entry
    copy = entry + "\n\n"

    content=""

    while len(copy) != 0 and not copy.isspace():

        # Deals with headings
        if copy[0] == '#':
            j = 0

            # Finds the number of '#' to get the heading level number
            while copy[j] == '#':
                j += 1

            # Substitutes the '#'s with the right heading tags
            copy = re.sub('##* ', f'<h{j}>', copy, 1)
            copy = re.sub('\s\s+', f'</h{j}>', copy, 1 )

            # Finds out the end of the identified heading
            split = re.search(f'</h{j}>', copy).end()

            sample = convert(copy[:split])

            # Adds the new heading to content and removes it from the entry copy
            content = content + sample
            copy = copy[split:]
            continue


        # Deals with making things bold
        if copy[:2] == '**':

            # Replaces the Markdown language with bold tags
            copy = copy.replace('**','<strong>', 1)
            copy = copy.replace('**','</strong>', 1)

            # Finds out the end of the identified bold phrase
            split = re.search('</strong>', copy).end()

            sample = convert(copy[:split])

            # Adds the bold phrase to content and removes it from the entry copy
            content = content + sample
            copy = copy[split:]
            continue

        # Also deals with making things bold another way
        if copy[:2] == '__':

            # Replaces the Markdown language with bold tags
            copy = copy.replace('__','<strong>', 1)
            copy = copy.replace('__','</strong>', 1)

            # Finds out the end of the identified bold phrase
            split = re.search('</strong>', copy).end()

            sample = convert(copy[:split])

            # Adds the bold phrase to content and removes it from the entry copy
            content = content + sample
            copy = copy[split:]
            continue

        # Deals with creating links
        if copy[0] == '[' and re.search('\[\S+\]', copy):

            # Gets the page the link is meant to lead to
            page = re.search('\(/wiki/\S+\)', copy).group(0)
            page = page[1:-1]

            # Replaces the Markdown language with anchor tags with the right href
            copy = copy.replace('[', f"<a href='{page}'>", 1)
            copy = re.sub(']\(/wiki/\S+\)', '</a>', copy, 1)

            # Finds out the end of the identified link
            split = re.search('</a>', copy).end()

            sample = convert(copy[:split])

            # Adds the link to content and removes it from the entry copy
            content = content + sample
            copy = copy[split:]
            continue

        
        # Deals with making unordered lists
        if copy[:2] in ['* ', '- ', '+ ']:
            content = content + '<ul>' 
            
            try:
                while copy[:2] in ['* ', '- ', '+ ']:

                    # Makes a phrase a list item if it has the correct Markdown syntax
                    copy = re.sub('[-+*] ', '<li>', copy, 1)
                    copy = re.sub('\s\s+', '</li>' , copy, 1)

                    # Finds out the end of the identified list
                    split = re.search('</li>', copy).end()

                    sample = convert(copy[:split])

                    # Adds the list item to content and removes it from the entry copy
                    content = content + sample
                    copy = copy[split:]

            except:
                continue
            
            # Closes the unordered list tag
            content = content +'</ul>'
            continue
        
        # Deals with making ordered lists
        if re.search('\d\. ', copy[:3]):
            content = content + '<ol>' 
            
            try:
                while re.search('\d\. ', copy[:3]):

                    # Makes a phrase a list item if it has the correct Markdown syntax
                    copy = re.sub('\d\. ', '<li>', copy, 1)
                    copy = re.sub('\s\s+', '</li>' , copy, 1)


                    # Finds out the end of the identified list
                    split = re.search('</li>', copy).end()

                    sample = convert(copy[:split])

                    # Adds the list item to content and removes it from the entry copy
                    content = content + sample
                    copy = copy[split:]
                
                # Closes the ordered list tag
                content = content +'</ol>'
                continue

            except:
                continue

        if copy[0] in ['\n', '\r'] and copy[1] not in ['\n', '\r']:
            content = content + '<br>'

        # Adds the current character to the content as no special editing must be done to it
        content = content + copy[:1]
        copy = copy[1:]
    
    return content
