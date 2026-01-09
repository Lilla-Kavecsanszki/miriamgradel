import os

from django.http import HttpResponse


def robots_txt(request):
    is_prod = os.getenv("ENV", "dev").lower() == "prod"

    if is_prod:
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
        # Block everything on staging
        content = "User-agent: *\nDisallow: /\n"

    return HttpResponse(content, content_type="text/plain")
