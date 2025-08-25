from django import template
from wagtail.models import Site
from behind_scenes.models import BTSPage, BTSIndexPage  # adjust if your app label differs

register = template.Library()

@register.simple_tag(takes_context=True)
def bts_teasers_for(context, category, limit=3):
    """
    Usage in templates:
      {% load bts_tags %}
      {% bts_teasers_for 'written' 3 as items %}
    """
    request = context.get("request")
    qs = BTSPage.objects.live().public().filter(category=category).select_related("teaser_image")

    # try to scope to the site's BTSIndexPage subtree
    try:
        site = Site.find_for_request(request) if request else Site.objects.get(is_default_site=True)
        root_page = site.root_page
        index = BTSIndexPage.objects.descendant_of(root_page, inclusive=True).live().first()
        if index:
            qs = qs.descendant_of(index)
    except Exception:
        pass

    return qs.order_by("-first_published_at")[:limit]
