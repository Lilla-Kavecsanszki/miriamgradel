from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.text import slugify

from .models import WorkWithMePage


def vcard_inline(request, page_id: int):
    page = get_object_or_404(WorkWithMePage, id=page_id)
    filename = f"{slugify(page.slug or 'contact')}.vcf"

    # Prefer uploaded file; otherwise synthesize a simple vCard
    content = b""
    if page.vcard_file:
        try:
            page.vcard_file.open("rb")
            content = page.vcard_file.read()
        finally:
            try:
                page.vcard_file.close()
            except Exception:
                pass
    else:
        full_name = page.title or "Contact"
        email = page.contact_email or ""
        phone = (page.phone_number or "").replace(" ", "")
        lines = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"FN:{full_name}",
        ]
        if email:
            lines.append(f"EMAIL;TYPE=INTERNET:{email}")
        if phone:
            lines.append(f"TEL;TYPE=CELL:{phone}")
        lines.append("END:VCARD")
        content = ("\r\n".join(lines) + "\r\n").encode("utf-8")

    if not content:
        raise Http404("No vCard available")

    resp = HttpResponse(content, content_type="text/vcard; charset=utf-8")
    # Inline for QR (phones show “Add to Contacts”); button can pass ?download=1
    disposition = "attachment" if request.GET.get("download") else "inline"
    resp["Content-Disposition"] = f'{disposition}; filename="{filename}"'
    return resp
