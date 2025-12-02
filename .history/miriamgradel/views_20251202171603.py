from django.conf import settings

def robots_txt(request):
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
        content = "User-agent: *\nDisallow: /\n"

    return HttpResponse(content, content_type="text/plain")
