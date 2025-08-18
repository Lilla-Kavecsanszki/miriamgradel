from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(label="Your name", max_length=120)
    email = forms.EmailField(label="Your email")
    subject = forms.CharField(label="Subject", max_length=150, required=False)
    message = forms.CharField(label="Message", widget=forms.Textarea(attrs={"rows": 6}))
    hp = forms.CharField(required=False, widget=forms.HiddenInput)  # honeypot
