# work_with_me/views.py
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.text import slugify

from .models import WorkWithMePage


def vcard_inline(request, page_id: int):
    """
    Serve a vCard as a file download (Content-Disposition: attachment).
    Phones then offer "Add to Contacts". If no file is uploaded, synthesize one.
    """
    page = get_object_or_404(WorkWithMePage, id=page_id)

    # 1) Prefer the uploaded .vcf bytes
    vcf_bytes = b""
    if page.vcard_file:
        try:
            f = page.vcard_file
            f.open("rb")
            vcf_bytes = f.read()
            f.close()
        except Exception:
            vcf_bytes = b""

    # 2) Fallback: synthesize a simple, valid VCARD (v3.0)
    if not vcf_bytes:
        name = page.title or "Contact"
        fn = name
        tel = (page.phone_number or "").replace(" ", "")
        email = page.contact_email or page.to_address or ""
        url = ""
        try:
            url = page.get_full_url()
        except Exception:
            pass

        lines = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"FN:{fn}",
            f"N:{fn};;;;",  # Last;First;Middle;Prefix;Suffix (simple)
        ]
        if tel:
            lines.append(f"TEL;TYPE=CELL,VOICE:{tel}")
        if email:
            lines.append(f"EMAIL;TYPE=INTERNET:{email}")
        if url:
            lines.append(f"URL:{url}")
        lines.append("END:VCARD")

        # vCard prefers CRLF line endings
        vcf_bytes = ("\r\n".join(lines) + "\r\n").encode("utf-8")

    filename = f"{slugify(page.slug or page.title or 'contact')}.vcf"

    # Use attachment to trigger the “open with Contacts / download” UX
    resp = HttpResponse(vcf_bytes, content_type="text/vcard; charset=utf-8")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    # (Optional) helps some Android browsers:
    resp["X-Content-Type-Options"] = "nosniff"
    return resp
