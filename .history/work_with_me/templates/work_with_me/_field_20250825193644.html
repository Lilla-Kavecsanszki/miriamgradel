from django import template
from django.utils.safestring import mark_safe

try:
    import segno
except Exception:
    segno = None

register = template.Library()

@register.simple_tag
def wme_qr_svg(data, scale=10, border=0):
    """
    Return inline SVG for a QR code (requires 'segno').
    Usage:
      {% wme_qr_svg page.get_qr_payload page.qr_scale as qr_svg %}
      {{ qr_svg|safe }}
    """
    if not data or segno is None:
        return ""
    q = segno.make(data, error="h")
    svg = q.svg_inline(scale=int(scale or 10), border=int(border or 0))
    return mark_safe(svg)
