from django.db import models
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from modelcluster.fields import ParentalKey
from wagtail.documents.models import Document


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
        "wagtailimages.Image",
        null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
    )
    phone_number = models.CharField(max_length=50, blank=True)

    thank_you_text = RichTextField(blank=True, help_text="Shown after a successful submission.")
    contact_email = models.EmailField(blank=True, help_text="Shown on the page")

    # --- QR fields ---
    # CHANGE: CharField -> TextField (vCards are long)
    qr_data = models.TextField(
        blank=True,
        help_text="Raw QR payload (vCard/URL/mailto/tel). If blank, will auto-generate."
    )
    qr_scale = models.PositiveSmallIntegerField(default=10, help_text="Size scale for the QR SVG")

    # NEW: attach a vCard file (Document)
    vcard_document = models.ForeignKey(
        Document, null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
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
            [FieldPanel("vcard_document"), FieldPanel("qr_data"), FieldPanel("qr_scale")],
            heading="QR options",
        ),
    ]

    def get_qr_payload(self):
        """
        Priority:
        1) qr_data if present (can be vCard or any raw text)
        2) mailto:contact_email if set
        3) fallback to page URL
        """
        if self.qr_data:
            return self.qr_data.strip()
        if self.contact_email:
            return f"mailto:{self.contact_email}"
        return self.get_full_url()

    def _read_vcard_document_text(self) -> str:
        """
        Safely read the attached .vcf (if any) as UTF-8 text.
        Returns '' if no document or read fails.
        """
        doc = self.vcard_document
        if not doc or not doc.file:
            return ""
        try:
            # .file is a Django File object; read bytes then decode
            data = doc.file.read()
            # Reset pointer so admin preview/download still works normally
            doc.file.seek(0)
            return data.decode("utf-8", errors="replace").strip()
        except Exception:
            return ""

    def save(self, *args, **kwargs):
        creating = self.pk is None

        # If a vCard file is attached, copy its contents into qr_data automatically.
        # (Let editors still override qr_data manually — only auto-fill when empty
        #  or when a new/changed vCard is present.)
        vcard_text = self._read_vcard_document_text()
        if vcard_text:
            # If qr_data is blank or clearly not a vCard yet, replace it.
            if not self.qr_data or self.qr_data.strip() == "" or "BEGIN:VCARD" in vcard_text:
                self.qr_data = vcard_text

        super().save(*args, **kwargs)

        # Seed default form fields if creating (same as your existing logic)
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
