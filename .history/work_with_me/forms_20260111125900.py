from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(label="name", max_length=120)
    email = forms.EmailField(label="email")
    subject = forms.CharField(max_length=150, required=False)
    message = forms.CharField(widget=forms.Textarea(attrs={"rows": 6}))
    hp = forms.CharField(required=False, widget=forms.HiddenInput)  # honeypot
