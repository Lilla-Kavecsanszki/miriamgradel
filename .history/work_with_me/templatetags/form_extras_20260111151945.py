from django import template
from django.utils.html import format_html

register = template.Library()


@register.filter(name="addcss")
def addcss(bound_field, css_class):
    """
    Render a bound field widget with extra CSS classes.

    Usage:
        {{ field|addcss:"form-control wme-input" }}
    """
    widget_attrs = bound_field.field.widget.attrs.copy()
    existing = widget_attrs.get("class", "")
    widget_attrs["class"] = f"{existing} {css_class}".strip() if existing else css_class
    return bound_field.as_widget(attrs=widget_attrs)


@register.simple_tag
def render_field(bound_field, **attrs):
    """
    Render a bound field with arbitrary HTML attrs.

    Usage:
        {% render_field field class="form-control wme-input" rows=8 placeholder="Type…" %}

    Notes:
    - Merges 'class' with any existing widget classes.
    - Preserves existing widget attrs unless overridden.
    - Treats boolean attrs correctly (True -> attribute present, False/None -> omitted).
    """
    widget_attrs = bound_field.field.widget.attrs.copy()

    # Merge CSS classes
    extra_class = attrs.pop("class", "")
    if extra_class:
        existing = widget_attrs.get("class", "")
        widget_attrs["class"] = f"{existing} {extra_class}".strip() if existing else extra_class

    # Apply remaining attrs (omit None/""/False; keep True as boolean attribute)
    for key, value in attrs.items():
        if value is None or value == "" or value is False:
            continue
        widget_attrs[key] = key if value is True else str(value)

    return format_html("{}", bound_field.as_widget(attrs=widget_attrs))
