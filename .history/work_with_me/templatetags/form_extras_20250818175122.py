from django import template

register = template.Library()

@register.filter
def addcss(field, css):
    attrs = field.field.widget.attrs
    existing = attrs.get("class", "")
    attrs = {**attrs, "class": (existing + " " + css).strip()}
    return field.as_widget(attrs=attrs)
