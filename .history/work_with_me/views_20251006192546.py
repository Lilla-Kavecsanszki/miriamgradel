# work_with_me/views.py
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.urls import reverse
import requests

from .models import WorkWithMePage


def vcard_inline(request, page_id: int):
    """
    Serve a .vcf as text/vcard with Content-Disposition: inline.
    Many phones will show an 'Add to contacts' prompt.
    """
    page = get_object_or_404(WorkWithMePage, id=page_id)

    content: bytes | None = None

    # 1) If a vCard file was uploaded, try to read it from storage…
    if page.vcard_file:
        try:
            with page.vcard_file.open("rb") as f:
                content = f.read()
        except Exception:
            # …or fall back to fetching the URL (Cloudinary RAW) over HTTP
            try:
                r = requests.get(page.vcard_file.url, timeout=10)
                r.raise_for_status()
                content = r.content
            except Exception:
                content = None

    # 2) If still no content, build a minimal vCard from fields
    if not content:
        name = page.title or "Contact"
        email = page.contact_email or ""
        tel = (page.phone_number or "").replace(" ", "")
        url = ""
        try:
            url = page.get_full_url()
        except Exception:
            url = page.url or ""

        vcf = f"""BEGIN:VCARD
VERSION:3.0
FN:{name}
EMAIL;TYPE=INTERNET:{email}
TEL;TYPE=CELL:{tel}
URL:{url}
END:VCARD
"""
        content = vcf.encode("utf-8")

    filename = f"{slugify(page.slug or page.title or 'contact')}.vcf"
    resp = HttpResponse(content, content_type="text/vcard; charset=utf-8")
    resp["Content-Disposition"] = f'inline; filename="{filename}"'
    resp["X-Robots-Tag"] = "noindex, nofollow"
    return resp
