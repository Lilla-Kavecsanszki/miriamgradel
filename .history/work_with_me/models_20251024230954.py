import os
import logging

from django.db import models
from django.urls import reverse
from django.contrib import messages

from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page, Site
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from modelcluster.fields import ParentalKey

logger = logging.getLogger(__name__)


# ---------------- Cloudinary RAW storage (optional) ----------------
VCARD_FILEFIELD_KW = dict(
    upload_to="vcards/",
    blank=True,
    null=True,
    help_text="Upload a .vcf (vCard). QR will link to this file if present.",
)

def _cloudinary_present() -> bool:
    return bool(
        os.getenv("CLOUDINARY_URL")
        or (
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


# ---------------- Form field ----------------
class WorkWithMeFormField(AbstractFormField):
    page = ParentalKey(
        "work_with_me.WorkWithMePage",
        on_delete=models.CASCADE,
        related_name="form_fields",
    )


# ---------------- Page ----------------
class WorkWithMePage(AbstractEmailForm):
    template = "work_with_me_page.html"
    landing_page_template = "work_with_me_page_landing.html"

    # --- fields (unchanged) ---
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

    # QR options
    qr_data = models.TextField(
        blank=True,
        help_text="Raw QR payload (URL / mailto: / tel: / vCard text). Leave blank to auto-generate.",
    )
    qr_scale = models.PositiveSmallIntegerField(default=10, help_text="Size scale for the QR SVG")

    # Optional vCard file (served via Cloudinary RAW when available)
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

    # ---------------- Helpers ----------------
    def _absolute_url(self, path_or_url: str) -> str:
        """Ensure an absolute URL for QR targets (force https)."""
        if not path_or_url:
            return ""
        if path_or_url.startswith(("http://", "https://")):
            return path_or_url
        try:
            site = Site.objects.get(is_default_site=True)
            host = site.hostname
            port = site.port
            scheme = "https"
            port_part = "" if port in (80, 443, None) else f":{port}"
            return f"{scheme}://{host}{port_part}{path_or_url}"
        except Exception:
            return path_or_url

    def get_qr_payload(self) -> str:
        """
        Default QR target: our inline vCard endpoint (a URL).
        """
        try:
            rel = reverse("work_with_me:vcard_inline", args=[self.id])
            return self._absolute_url(rel)
        except Exception:
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

    # === what the QR *encodes* (prefer embedded vCard text) ===
    def get_qr_image_payload(self) -> str:
        """
        If admin pasted a vCard (BEGIN:VCARD...), embed that text directly (CRLF),
        otherwise fall back to the URL endpoint.
        """
        if self.qr_data and self.qr_data.lstrip().upper().startswith("BEGIN:VCARD"):
            v = self.qr_data.strip().replace("\r\n", "\n").replace("\n", "\r\n")
            return v
        return self.get_qr_payload()  # URL fallback

    # === what the <a href="..."> should be when clicking the QR image ===
    def get_qr_click_href(self) -> str:
        """
        Always return a URL (never raw vCard text) for clickable links on the page.
        """
        try:
            rel = reverse("work_with_me:vcard_inline", args=[self.id])
            return self._absolute_url(rel)
        except Exception:
            if self.vcard_file:
                return self._absolute_url(self.vcard_file.url)
            return self._absolute_url(self.url or "/")

    # ---------------- Form handling override ----------------
    def process_form_submission(self, form):
        """
        Handle the form submit safely:
        - always save the submission to the DB
        - try to send email, but don't crash if it fails
        - attach a user-visible message (success or error)
        - then render the landing page
        """

        # 1. Save the submission (same thing Wagtail does internally)
        submission_class = self.get_submission_class()
        submission = submission_class.objects.create(
            form_data=form.cleaned_data,
            page=self,
        )

        # 2. Try to send the notification email
        try:
            self.send_mail(form)
            messages.success(
                form.request,
                "Thank you — your message was sent successfully."
            )
        except Exception as e:
            # Log the full traceback to Heroku logs
            logger.exception("WorkWithMePage email send failed: %s", e)

            # Show a friendly, branded error to the user (no tech details)
            messages.error(
                form.request,
                "Sorry — something went wrong sending your message. "
                "Your message was received, but email delivery failed. "
                "You can also contact me directly at contact@miriamgradel.cc."
            )

        # 3. Return the landing / thank-you response
        return self.render_landing_page(form, form.request, submission)
