from django.conf import settings
from django.http import HttpResponse


def robots_txt(request):
    """
    Dynamic robots.txt:
    - DEBUG: block everything
    - Production: allow crawling, block AI crawlers
    """
    if settings.DEBUG:
        # In local/dev: prevent indexing entirely
        content = "User-agent: *\nDisallow: /\n"
    else:
        sitemap_url = request.build_absolute_uri("/sitemap.xml")

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
            f"Sitemap: {sitemap_url}\n"
        )

    return HttpResponse(content, content_type="text/plain")
