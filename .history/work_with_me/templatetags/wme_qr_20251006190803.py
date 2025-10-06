from django import template
from django.utils.safestring import mark_safe

try:
    import segno
except Exception:
    segno = None

register = template.Library()

@register.simple_tag
def wme_qr_svg(data, scale=10, border=None):
    """
    Return inline SVG for a QR code (requires 'segno').
    """
    if not data or segno is None:
        return ""
    q = segno.make(data, error="h")
    # Quiet zone: default to 4 modules if not given
    border = 4 if border is None else int(border)
    svg = q.svg_inline(
        scale=int(scale or 10),
        border=border,
        dark="black",
        light="white",   # ensures the quiet zone is actually white
    )
    return mark_safe(svg)
