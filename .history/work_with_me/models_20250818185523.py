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


class WorkWithMePage(AbstractEmailForm):  # don't inherit Page again
    template = "work_with_me_page.html"
    landing_page_template = "work_with_me_page_landing.html"

    # Content
    greeting = models.CharField(max_length=200, blank=True)
    intro = RichTextField(blank=True)

    bold_text = models.CharField(max_length=200, blank=True)
    paragraph = RichTextField(blank=True, features=["bold", "italic", "link"])

    portrait = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
    )
    phone_number = models.CharField(max_length=50, blank=True)

    thank_you_text = RichTextField(blank=True, help_text="Shown after a successful submission.")
    contact_email = models.EmailField(blank=True, help_text="Shown on the page")

    # QR (auto-generate)
    qr_data = models.CharField(
        max_length=300, blank=True,
        help_text="Text/URL to encode. Leave blank to auto-use mailto:contact_email"
    )
    qr_scale = models.PositiveSmallIntegerField(default=10, help_text="Size scale for the QR SVG")

    content_panels = Page.content_panels + [
        FieldPanel("greeting"),
        FieldPanel("intro"),
        FieldPanel("bold_text"),
        FieldPanel("paragraph"),
        FieldPanel("portrait"),
        FieldPanel("phone_number"),
        FieldPanel("contact_email"),
        FieldPanel("thank_you_text"),

        InlinePanel("form_fields", label="Form fields"),

        MultiFieldPanel(
            [FieldPanel("from_address"), FieldPanel("to_address"), FieldPanel("subject")],
            heading="Email settings (used for notifications)",
        ),
        MultiFieldPanel(
            [FieldPanel("qr_data"), FieldPanel("qr_scale")],
            heading="QR auto-generate",
        ),
    ]

    def get_qr_payload(self):
        if self.qr_data:
            return self.qr_data.strip()
        if self.contact_email:
            return f"mailto:{self.contact_email}"
        return self.get_full_url()

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)
        if creating and not self.form_fields.exists():
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
