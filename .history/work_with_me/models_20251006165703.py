import os

from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.fields import RichTextField
from wagtail.models import Page, Site

# -------------------------------------------------------------------
# Cloudinary RAW storage for .vcf (robust with fallback)
# -------------------------------------------------------------------
# --- Cloudinary RAW storage for .vcf (robust with fallback) ---
VCARD_FILEFIELD_KW = dict(
    upload_to="vcards/",
    blank=True,
    null=True,
    help_text="Upload a .vcf (vCard). QR will link to this file if present.",
)

def _cloudinary_present() -> bool:
    return bool(
        os.getenv("CLOUDINARY_URL") or (
            os.getenv("CLOUDINARY_CLOUD_NAME")
            and os.getenv("CLOUDINARY_API_KEY")
            and os.getenv("CLOUDINARY_API_SECRET")
        )
    )

VCardRawStorage = None
if _cloudinary_present():
    try:
        from cloudinary_storage.storage import RawMediaCloudinaryStorage
        VCardRawStorage = RawMediaCloudinaryStorage
    except Exception:
        try:
            from cloudinary_storage.storage import MediaCloudinaryStorage
            class VCardRawStorage(MediaCloudinaryStorage):  # type: ignore
                resource_type = "raw"
        except Exception:
            VCardRawStorage = None

if VCardRawStorage:
    VCARD_FILEFIELD_KW["storage"] = VCardRawStorage()

# -------------------------------------------------------------------
# Form field
# -------------------------------------------------------------------
class WorkWithMeFormField(AbstractFormField):
    page = ParentalKey(
        "work_with_me.WorkWithMePage",
        on_delete=models.CASCADE,
        related_name="form_fields",
    )


# -------------------------------------------------------------------
# Page
# -------------------------------------------------------------------
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
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    phone_number = models.CharField(max_length=50, blank=True)

    thank_you_text = RichTextField(blank=True)
    contact_email = models.EmailField(blank=True, help_text="Shown on the page")

    # QR options
    qr_data = models.TextField(
        blank=True,
        help_text="Raw QR payload (URL / mailto: / tel: / vCard text). Leave blank to auto-generate.",
    )
    qr_scale = models.PositiveSmallIntegerField(
        default=10, help_text="Size scale for the QR SVG"
    )

    # vCard file (served via Cloudinary RAW when available)
    vcard_file = models.FileField(**VCARD_FILEFIELD_KW)

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

    # ----------------------
    # Helpers
    # ----------------------
    def _absolute_url(self, path_or_url: str) -> str:
        """
        Ensure an absolute URL. Cloudinary returns absolute URLs;
        local media may be relative (e.g. /media/...).
        """
        if not path_or_url:
            return ""
        if path_or_url.startswith(("http://", "https://")):
            return path_or_url
        try:
            site = Site.objects.get(is_default_site=True)
            root = (site.root_url or "").rstrip("/")
            return f"{root}{path_or_url}"
        except Exception:
            return path_or_url

    def get_qr_payload(self) -> str:
        """
        Choose the most useful payload for the QR:
        1) vCard file URL (best)
        2) Manually-entered qr_data
        3) mailto: / tel:
        4) Page URL
        """
        if self.vcard_file:
            return self._absolute_url(self.vcard_file.url)

        if self.qr_data:
            return self.qr_data.strip()

        if self.contact_email:
            return f"mailto:{self.contact_email}"

        if self.phone_number:
            return f"tel:{self.phone_number.replace(' ', '')}"

        try:
            return self.get_full_url()
        except Exception:
            return self.url or "/"

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)

        # Seed sensible default form fields on first create
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
