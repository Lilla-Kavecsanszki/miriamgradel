from django import template
from django.utils.safestring import mark_safe

try:
    import segno
except Exception:
    segno = None

# PNG support (via pypng). If missing, PNG fallback quietly disables itself.
try:
    import png as _pypng  # noqa: F401
    _HAS_PNG = True
except Exception:
    _HAS_PNG = False

register = template.Library()


@register.simple_tag
def wme_qr_svg(data, scale=8, border=4, dark="#000000", light="#ffffff"):
    """
    Inline SVG QR with quiet zone + high contrast.
    Usage:
      {% wme_qr_svg payload 8 4 as qr_svg %}  -> {{ qr_svg|safe }}
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


@register.simple_tag
def wme_qr_png_data_uri(data, scale=8, border=4):
    """
    PNG data-URI fallback (requires pypng). Returns "" if pypng is not installed.
    Usage:
      {% wme_qr_png_data_uri payload 8 4 as qr_png %} -> <img src="{{ qr_png }}">
    """
    if not data or segno is None or not _HAS_PNG:
        return ""
    q = segno.make(data, error="h")
    return q.png_data_uri(scale=int(scale or 8), border=int(border or 4))
