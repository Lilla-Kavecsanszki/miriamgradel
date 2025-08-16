from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.images.models import Image
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from modelcluster.fields import ParentalKey


# Form fields that editors add in the CMS (Name, Family name, Email, Subject, Message)
class WorkWithMeFormField(AbstractFormField):
    page = ParentalKey(
        "work_with_me.WorkWithMePage",
        on_delete=models.CASCADE,
        related_name="form_fields",
    )


class WorkWithMePage(AbstractEmailForm):
    """
    Contact / Work With Me page with:
    - Greeting + intro on the left above the form
    - Wagtail email form (left)
    - Portrait, QR and contact details (right)
    """

    template = "work_with_me/work_with_me_page.html"

    # Left column content
    greeting_title = models.CharField(
        max_length=160,
        default="Hello! My name is Miriam Gradel. Nice to e-meet you.",
        help_text="The top banner title."
    )
    intro_heading = models.CharField(
        max_length=120,
        default="15 years of Journalism",
        help_text="Heading shown above the intro body."
    )
    intro_body = RichTextField(
        blank=True,
        help_text="Introductory text above the contact form."
    )
    form_heading = models.CharField(
        max_length=120,
        default="Let’s discuss together",
        help_text="Heading shown above the form."
    )

    # Right column content
    portrait_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    contact_heading = models.CharField(
        max_length=120,
        default="Contact details",
        blank=True,
    )
    qr_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional QR image (e.g., vCard / link)."
    )
    phone_display = models.CharField(
        max_length=120,
        blank=True,
        help_text="Shown as-is, e.g. +45 12 34 56 78"
    )
    email_display = models.EmailField(
        blank=True,
        help_text="Shown as-is; also used as a mailto link."
    )

    # Email settings (Wagtail form)
    thank_you_text = RichTextField(blank=True)

    content_panels = [
        FieldPanel("greeting_title"),
        FieldPanel("intro_heading"),
        FieldPanel("intro_body"),
        FieldPanel("form_heading"),

        InlinePanel("form_fields", label="Form fields"),

        FieldPanel("thank_you_text"),

        MultiFieldPanel(
            [
                FieldPanel("to_address"),
                FieldPanel("from_address"),
                FieldPanel("subject"),
            ],
            heading="Email settings",
        ),

        FieldPanel("portrait_image"),
        FieldPanel("contact_heading"),
        FieldPanel("qr_image"),
        FieldPanel("phone_display"),
        FieldPanel("email_display"),
    ]
