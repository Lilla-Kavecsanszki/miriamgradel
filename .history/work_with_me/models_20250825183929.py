# work_with_me/models.py
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.fields import RichTextField
from wagtail.models import Page


class WorkWithMeFormField(AbstractFormField):
    page = ParentalKey(
        "work_with_me.WorkWithMePage",
        on_delete=models.CASCADE,
        related_name="form_fields",
    )

class WorkWithMePage(AbstractEmailForm):
    template = "work_with_me_page.html"
    landing_page_template = "work_with_me_page_landing.html"

    # Content
    greeting = models.CharField(max_length=200, blank=True)
    intro = RichTextField(blank=True)
    bold_text = models.CharField(max_length=200, blank=True)
    paragraph = RichTextField(blank=True, features=["bold", "italic", "link"])

    portrait = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    phone_number = models.CharField(max_length=50, blank=True)

    thank_you_text = RichTextField(blank=True)
    contact_email = models.EmailField(blank=True, help_text="Shown on the page")

    # QR
    qr_data = models.TextField(
        blank=True,
        help_text="Raw QR payload (vCard/URL/mailto/tel). If blank, will auto-generate."
    )
    qr_scale = models.PositiveSmallIntegerField(default=10, help_text="Size scale for the QR SVG")

    # 🔹 NEW: page-local file upload that accepts .vcf
    vcard_file = models.FileField(
        upload_to="vcards/", blank=True, null=True,
        help_text="Upload a .vcf (vCard). The file contents will auto-fill the QR payload."
    )

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
            [FieldPanel("vcard_file"), FieldPanel("qr_data"), FieldPanel("qr_scale")],
            heading="QR options",
        ),
    ]

    # --- helpers ---
    def _read_vcard_text(self) -> str:
        f = self.vcard_file
        if not f:
            return ""
        try:
            data = f.read()
            f.seek(0)
            return data.decode("utf-8", errors="replace").strip()
        except Exception:
            return ""

    def get_qr_payload(self):
        if self.qr_data:
            return self.qr_data.strip()
        if self.contact_email:
            return f"mailto:{self.contact_email}"
        return self.get_full_url()

    def save(self, *args, **kwargs):
        creating = self.pk is None

        # If a vCard file is attached, prefer it to populate qr_data
        vcard_text = self._read_vcard_text()
        if vcard_text:
            self.qr_data = vcard_text

        super().save(*args, **kwargs)

        if creating and not self.form_fields.exists():
            WorkWithMeFormField.objects.create(page=self, label="Your name", field_type="singleline", required=True)
            WorkWithMeFormField.objects.create(page=self, label="Your email", field_type="email", required=True)
            WorkWithMeFormField.objects.create(page=self, label="Subject", field_type="singleline", required=False)
            WorkWithMeFormField.objects.create(page=self, label="Message", field_type="multiline", required=True)
