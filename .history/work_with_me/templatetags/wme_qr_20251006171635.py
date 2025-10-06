from django import template
from django.utils.safestring import mark_safe

try:
    import segno
except Exception:
    segno = None

register = template.Library()

@register.simple_tag
def wme_qr_svg(data, scale=8, border=4, dark="#000000", light="#ffffff"):
    """
    Inline SVG QR with a proper quiet zone and high contrast.
    Usage:
      {% wme_qr_svg page.get_qr_payload 8 4 as qr_svg %}  {# scale=8, border=4 #}
      {{ qr_svg|safe }}
    """
    if not data or segno is None:
        return ""
    q = segno.make(data, error="h")
    svg = q.svg_inline(
        scale=int(scale or 8),
        border=int(border or 4),   # quiet zone
        dark=dark,
        light=light,               # solid white background
    )
    return mark_safe(svg)
