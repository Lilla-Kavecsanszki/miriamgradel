from django.conf import settings
from django.http import HttpResponse


def robots_txt(request):
    """
    Dynamic robots.txt:
    - In DEBUG: block everything
    - In production: allow normal crawling but block AI crawlers
    """
    if not settings.DEBUG:
        content = (
            "User-agent: GPTBot\n"
            "Disallow: /\n\n"
            "User-agent: CCBot\n"
            "Disallow: /\n\n"
            "User-agent: Amazonbot\n"
            "Disallow: /\n\n"
            "User-agent: ClaudeBot\n"
            "Disallow: /\n\n"
            "User-agent: *\n"
            "Allow: /\n"
            f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}\n"
        )
    else:
        # In local/dev: keep it fully blocked so search engines don't index dev
        content = "User-agent: *\nDisallow: /\n"

    return HttpResponse(content, content_type="text/plain")

