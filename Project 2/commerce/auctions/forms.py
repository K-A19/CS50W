from django import forms

class NewListingForm(forms.Form):
    title = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'placeholder': 'Title'}), label='', required=True)
    description = forms.CharField(max_length=500, widget=forms.Textarea(attrs={'placeholder': 'Description'}), label='', required=True)
    bid = forms.DecimalField(max_digits=6, decimal_places=2, widget=forms.NumberInput(attrs={'placeholder': 'Minimum Bid', 'min' : '0.01'}), label='', required=True)
    image = forms.URLField(widget=forms.URLInput(attrs={'placeholder': 'Image Url (Optional)'}), label='', required=False)
    category = forms.CharField(max_length=64, required=False, widget=forms.TextInput(attrs={'placeholder': 'Category (Optional)'}), label='' )


class NewBidForm(forms.Form):
    bid = forms.DecimalField(max_digits=6, decimal_places=2, widget=forms.NumberInput(attrs={'placeholder': 'Make Bid', 'min' : '0.01'}), label='', required=True)