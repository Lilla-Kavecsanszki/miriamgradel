from django import template
from django.utils.html import format_html

register = template.Library()

@register.filter
def addcss(field, css):
    """(You already have this)"""
    return field.as_widget(attrs={'class': css})

@register.simple_tag
def render_field(field, **attrs):
    """
    Render a bound field with arbitrary HTML attrs.
    Usage:
      {% render_field field class="form-control wme-input" rows=8 placeholder="Type…" %}
    - Merges 'class' with any existing widget classes.
    """
    widget = field.field.widget
    merged = widget.attrs.copy()
    # Merge classes
    if 'class' in attrs:
        merged['class'] = (merged.get('class', '') + ' ' + attrs.pop('class')).strip()
    merged.update({k: str(v) for k, v in attrs.items() if v is not None and v != ''})
    return format_html("{}", field.as_widget(attrs=merged))
