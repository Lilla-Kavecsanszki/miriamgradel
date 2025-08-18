# work_with_me/models.py
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from django.db import models

from .forms import ContactForm


class WorkWithMePage(Page):
    template = "work_with_me_page.html"

    greeting = models.CharField(max_length=200, blank=True)
    intro = RichTextField(blank=True)
    portrait = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    contact_email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=50, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("greeting"),
        FieldPanel("intro"),
        FieldPanel("portrait"),
        FieldPanel("contact_email"),
        FieldPanel("phone_number"),
    ]

    # Handle GET/POST so we can keep this as a normal Page type
    def serve(self, request):
        form = ContactForm(request.POST or None)

        if request.method == "POST" and form.is_valid():
            # simple spam trap
            if form.cleaned_data.get("hp"):
                return redirect(f"{self.url}?sent=1")

            to_email = self.contact_email or getattr(settings, "DEFAULT_FROM_EMAIL", None)
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com")

            if to_email:
                subj = form.cleaned_data["subject"] or f"Website enquiry from {form.cleaned_data['name']}"
                body = (
                    f"New enquiry from {form.cleaned_data['name']} <{form.cleaned_data['email']}> \n\n"
                    f"Subject: {form.cleaned_data['subject'] or '(no subject)'}\n\n"
                    f"Message:\n{form.cleaned_data['message']}\n"
                )
                # Use reply_to so you can reply directly to the sender
                send_mail(subject=subj, message=body, from_email=from_email, recipient_list=[to_email],
                          fail_silently=False, reply_to=[form.cleaned_data["email"]])

            # PRG pattern to avoid resubmits
            return redirect(f"{self.url}?sent=1")

        context = self.get_context(request)
        context["form"] = form
        context["sent"] = request.GET.get("sent") == "1"
        return render(request, self.template, context)
