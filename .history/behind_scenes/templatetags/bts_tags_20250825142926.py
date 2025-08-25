# bts/templatetags/bts_tags.py
from django import template
from wagtail.models import Site
from behind_scenes.models import BTSPage, BTSIndexPage  # adjust import path if needed

register = template.Library()

@register.simple_tag(takes_context=True)
def bts_teasers_for(context, category, limit=3):
    """
    Usage:
      {% bts_teasers_for 'written' 3 as bts_items %}
    Returns BTSPage queryset filtered by category,
    preferably scoped under the site's BTSIndexPage (if present).
    """
    request = context.get("request")
    qs = BTSPage.objects.live().public().filter(category=category).select_related("teaser_image")

    # If there is a BTSIndexPage on this Site, scope to its descendants
    try:
        site = Site.find_for_request(request) if request else Site.get_site_root_paths()[0]
        root_page = site.root_page if request else Site.objects.get(is_default_site=True).root_page
        # Find the BTSIndexPage under the site tree (first one wins)
        index = BTSIndexPage.objects.descendant_of(root_page, inclusive=True).live().first()
        if index:
            qs = qs.descendant_of(index)
    except Exception:
        pass

    return qs.order_by("-first_published_at")[:limit]
