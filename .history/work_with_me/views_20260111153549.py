from __future__ import annotations

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.text import slugify

from .models import WorkWithMePage


def _normalize_vcard_text(text: str) -> str:
    """
    Ensure vCard uses CRLF line endings and ends with a trailing CRLF.

    vCard specs expect CRLF. We normalize any input to CRLF and add one final CRLF.
    """
    if not text:
        return ""

    # Normalize any line endings to LF, trim trailing blank lines,
    # then convert back to CRLF.
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip("\n")
    return normalized.replace("\n", "\r\n") + "\r\n"


def _decode_vcard_bytes(raw: bytes) -> str:
    """
    Decode a vCard file as text.

    Prefer UTF-8, fall back to latin-1 (common in older vCards) while
    preserving as much content as possible.
    """
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def vcard_inline(request, page_id: int) -> HttpResponse:
    """
    Stream a vCard. Order of preference:
      1) vCard pasted in qr_data (BEGIN:VCARD...),
      2) uploaded .vcf file,
      3) synthesized minimal card.
    """
    page = get_object_or_404(WorkWithMePage, id=page_id)
    filename = f"{slugify(page.slug or 'contact')}.vcf"

    # 1) Prefer vCard text in admin (qr_data)
    if page.qr_data and page.qr_data.lstrip().upper().startswith("BEGIN:VCARD"):
        content_str = _normalize_vcard_text(page.qr_data.strip())

    # 2) Else, use uploaded file (decode + normalize)
    elif page.vcard_file:
        try:
            with page.vcard_file.open("rb") as file_obj:
                raw = file_obj.read()
        except OSError as exc:
            raise Http404("vCard file not available") from exc

        decoded = _decode_vcard_bytes(raw)
        content_str = _normalize_vcard_text(decoded)

    # 3) Else, synthesize a minimal vCard
    else:
        full_name = (page.title or "Contact").strip()
        email = (page.contact_email or "").strip()
        phone = (page.phone_number or "").replace(" ", "").strip()

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

    response = HttpResponse(content_str, content_type="text/vcard; charset=utf-8")

    # Inline by default; allow forced download with ?download=1|true|yes
    dl_param = (request.GET.get("download") or "").lower()
    disposition = "attachment" if dl_param in {"1", "true", "yes"} else "inline"
    response["Content-Disposition"] = f'{disposition}; filename="{filename}"'
    response["X-Content-Type-Options"] = "nosniff"

    # Cache: only cache aggressively if this is generated from stable sources.
    # If using qr_data (editable in admin), you may prefer to reduce caching.
    response["Cache-Control"] = "public, max-age=3600"

    return response
