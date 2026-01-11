from __future__ import annotations

from django import template
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe

try:
    import segno
except ImportError:
    segno = None  # type: ignore[assignment]

register = template.Library()


def _to_int(value, default: int) -> int:
    """Best-effort int conversion with a fallback."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@register.simple_tag
def wme_qr_svg(data, scale=10, border=None, title=None):
    """
    Return inline SVG for a QR code (requires 'segno').

    Usage:
        {% wme_qr_svg page.get_qr_payload page.qr_scale 4 "Add contact" as qr_svg %}
        {{ qr_svg|safe }}
    """
    if not data or segno is None:
        return ""

    qr = segno.make(data, error="h")

    border_int = 4 if border is None else _to_int(border, 4)
    scale_int = _to_int(scale, 10)

    svg = qr.svg_inline(
        scale=scale_int,
        border=border_int,
        dark="black",
        light="white",
        title=title or "Scan QR",
    )

    # segno returns SVG markup; we intentionally return it as safe for template output.
    return mark_safe(svg)


@register.simple_tag
def wme_qr_png(data, scale=8, border=8, title="Scan QR"):
    """
    Return an <img> tag with a PNG data URI QR (more robust on some devices).

    Usage:
        {% wme_qr_png page.get_qr_payload 10 8 "Add contact" as qr_img %}
        {{ qr_img|safe }}
    """
    if not data or segno is None:
        return ""

    qr = segno.make(data, error="h")

    scale_int = _to_int(scale, 8)
    border_int = _to_int(border, 8)
    alt_text = title or "Scan QR"

    uri = qr.png_data_uri(
        scale=scale_int,
        border=border_int,
        dark="black",
        light="white",
    )

    # Use format_html so attributes are escaped safely.
    # (Data URI remains intact; alt text is escaped.)
    return format_html(
        '<img src="{}" alt="{}" decoding="async" loading="eager">',
        uri,
        alt_text,
    )
