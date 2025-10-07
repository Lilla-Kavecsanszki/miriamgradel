# work_with_me/templatetags/wme_qr.py
from django import template
from django.utils.safestring import mark_safe

try:
    import segno
except Exception:
    segno = None

register = template.Library()

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
    q = segno.make(data, error="h")

    border = 4 if border is None else int(border)

    svg = q.svg_inline(
        scale=int(scale or 10),
        border=border,
        dark="black",
        light="white",
        title=title or "Scan QR",
    )
    return mark_safe(svg)

# work_with_me/templatetags/wme_qr.py

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
    q = segno.make(data, error="h")
    # Create a data URI for a PNG
    uri = q.png_data_uri(scale=int(scale or 8), border=int(border or 8), dark="black", light="white")
    alt = title or "Scan QR"
    html = f'<img src="{uri}" alt="{alt}" decoding="async" loading="eager" />'
    return mark_safe(html)
