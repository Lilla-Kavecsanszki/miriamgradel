import os
import logging

from django.db import models
from django.urls import reverse
from django.contrib import messages

from django.shortcuts import render  # only used indirectly via self.render
from wagtail.admin.panels import FieldPanel, MultiFieldPanel  # InlinePanel removed
from wagtail.fields import RichTextField
from wagtail.models import Page, Site
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from modelcluster.fields import ParentalKey

from .forms import ContactForm  # <-- use your own static form

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


# ---------------- (Kept for compatibility, but not used by the page) ----------------
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
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    phone_number = models.CharField(max_length=50, blank=True)
    thank_you_text = RichTextField(blank=True)
    contact_email = models.EmailField(
        blank=True,
        help_text="Shown on the page",
    )

    # QR options
    qr_data = models.TextField(
        blank=True,
        help_text=(
            "Raw QR payload (URL / mailto: / tel: / vCard text). "
            "Leave blank to auto-generate."
        ),
    )
    qr_scale = models.PositiveSmallIntegerField(
        default=10,
        help_text="Size scale for the QR SVG",
    )

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
        # InlinePanel("form_fields", ...)  # <-- removed; we use ContactForm instead
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

    # === what the QR *encodes* (prefer embedded vCard text) ===
    def get_qr_image_payload(self) -> str:
        """
        If admin pasted a vCard (BEGIN:VCARD...), embed that text directly (CRLF),
        otherwise fall back to the URL endpoint.
        """
        if self.qr_data and self.qr_data.lstrip().upper().startswith("BEGIN:VCARD"):
            v = (
                self.qr_data.strip()
                .replace("\r\n", "\n")
                .replace("\n", "\r\n")
            )
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

    # ---------------- Form handling (uses your ContactForm) ----------------
    def serve(self, request, *args, **kwargs):
        """
        Custom GET/POST handler using the static ContactForm from forms.py
        """
        if request.method == "POST":
            form = ContactForm(request.POST)

            # Honeypot (optional): treat any value as spam
            if getattr(form, "is_valid", None) and form.is_valid():
                hp_value = form.cleaned_data.get("hp")
                if hp_value:
                    # Pretend success to bots; do nothing
                    messages.success(request, "Thank you — your message was sent successfully.")
                    return self.render_landing_page(request, None)

                # Save submission (optional but nice to keep Wagtail's history)
                self.get_submission_class().objects.create(
                    form_data=form.cleaned_data,
                    page=self,
                )

                # Try to send email via AbstractEmailForm
                try:
                    self.send_mail(form)
                    messages.success(
                        request,
                        "Thank you — your message was sent successfully."
                    )
                except Exception as e:
                    logger.exception("WorkWithMePage email send failed: %s", e)
                    messages.error(
                        request,
                        "Sorry — something went wrong sending your message. "
                        "You can also contact me directly at contact@miriamgradel.cc."
                    )

                # Landing / thank-you page
                return self.render_landing_page(request, None)
            else:
                messages.error(request, "Please correct the highlighted fields and try again.")
        else:
            form = ContactForm()

        context = self.get_context(request)
        context["form"] = form
        return self.render(request, context)
