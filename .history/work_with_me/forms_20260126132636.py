from django import forms


class ContactForm(forms.Form):
    first_name = forms.CharField(
        label="First name",
        max_length=60,
        strip=True,
    )
    surname = forms.CharField(
        label="Surname",
        max_length=60,
        strip=True,
        required=False,
    )
    your_email = forms.EmailField(
        label="Your email",
    )
    subject = forms.CharField(
        label="Subject",
        max_length=150,
        required=False,
        strip=True,
    )
    message = forms.CharField(
        label="Message",
        max_length=5000,
        widget=forms.Textarea(attrs={"rows": 6}),
        strip=True,
    )
    hp = forms.CharField(
        required=False,
        widget=forms.HiddenInput,
    )  # honeypot

    def clean_hp(self):
        """Reject spam bots that fill hidden fields."""
        value = (self.cleaned_data.get("hp") or "").strip()
        if value:
            raise forms.ValidationError("Invalid submission.")
        return value
