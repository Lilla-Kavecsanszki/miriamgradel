from django.db import models
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from modelcluster.fields import ParentalKey


class WorkWithMeFormField(AbstractFormField):
    page = ParentalKey(
        "work_with_me.WorkWithMePage",
        on_delete=models.CASCADE,
        related_name="form_fields",
    )


class WorkWithMePage(AbstractEmailForm, Page):
    template = "work_with_me_page.html"
    landing_page_template = "work_with_me_page_landing.html"

    # Content
    greeting = models.CharField(max_length=200, blank=True)
    intro = RichTextField(blank=True)

    paragraph = RichTextField(blank=True)
    bold_text = models.CharField(max_length=200, blank=True)
    
    portrait = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
    )
    phone_number = models.CharField(max_length=50, blank=True)

    # Optional: text to show on the landing/thank-you page
    thank_you_text = RichTextField(
        blank=True,
        help_text="Shown after a successful submission.",
    )

    # (Optional) Public contact email to display on the page
    contact_email = models.EmailField(blank=True, help_text="Shown on the page")

    content_panels = Page.content_panels + [
        FieldPanel("greeting"),
        FieldPanel("intro"),
        FieldPanel("portrait"),
        FieldPanel("phone_number"),
        FieldPanel("contact_email"),
        FieldPanel("thank_you_text"),
        InlinePanel("form_fields", label="Form fields"),
        MultiFieldPanel(
            [
                FieldPanel("from_address"),
                FieldPanel("to_address"),
                FieldPanel("subject"),
            ],
            heading="Email settings (used for notifications)",
        ),
    ]

    # (Nice-to-have) Seed default fields on first create
    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)
        if creating and not self.form_fields.exists():
            # Default fields: Name / Email / Subject / Message
            WorkWithMeFormField.objects.create(
                page=self, label="Your name", field_type="singleline", required=True
            )
            WorkWithMeFormField.objects.create(
                page=self, label="Your email", field_type="email", required=True
            )
            WorkWithMeFormField.objects.create(
                page=self, label="Subject", field_type="singleline", required=False
            )
            WorkWithMeFormField.objects.create(
                page=self, label="Message", field_type="multiline", required=True
            )
