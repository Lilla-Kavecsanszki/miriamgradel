from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.text import slugify

from .models import WorkWithMePage


def _normalize_vcard_text(text: str) -> str:
    """
    Ensure VCARD uses CRLF line endings and ends with a trailing CRLF.
    """
    if not text:
        return ""
    # Normalize to LF, then to CRLF
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.strip("\n")
    text = text.replace("\n", "\r\n")
    return text + "\r\n"


def vcard_inline(request, page_id: int):
    """
    Stream a vCard. Order of preference:
      1) vCard pasted in qr_data (BEGIN:VCARD...),
      2) uploaded .vcf file,
      3) synthesized minimal card.
    """
    page = get_object_or_404(WorkWithMePage, id=page_id)
    filename = f"{slugify(page.slug or 'contact')}.vcf"

    content_str = ""  # We'll build a text vCard and return as UTF-8

    # 1) Prefer vCard text in admin (qr_data)
    if page.qr_data and page.qr_data.lstrip().upper().startswith("BEGIN:VCARD"):
        content_str = _normalize_vcard_text(page.qr_data.strip())

    # 2) Else, use uploaded file (decode + normalize)
    elif page.vcard_file:
        try:
            with page.vcard_file.open("rb") as f:
                raw = f.read()
            try:
                decoded = raw.decode("utf-8")
            except UnicodeDecodeError:
                decoded = raw.decode("latin-1", errors="ignore")
            content_str = _normalize_vcard_text(decoded)
        except Exception as e:
            raise Http404("vCard file not available") from e

    # 3) Else, synthesize a minimal vCard
    else:
        full_name = page.title or "Contact"
        email = (page.contact_email or "").strip()
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
        content_str = _normalize_vcard_text("\n".join(lines))

    if not content_str:
        raise Http404("No vCard available")

    # Build response
    resp = HttpResponse(content_str, content_type="text/vcard; charset=utf-8")

    # Inline by default (better UX on mobile); allow forced download with ?download=1
    dl_param = (request.GET.get("download") or "").lower()
    disposition = "attachment" if dl_param in ("1", "true", "yes") else "inline"
    resp["Content-Disposition"] = f'{disposition}; filename="{filename}"'

    # Helpful cache headers for a static-ish contact card
    resp["Cache-Control"] = "public, max-age=31536000, immutable"
    resp["X-Content-Type-Options"] = "nosniff"

    return resp
