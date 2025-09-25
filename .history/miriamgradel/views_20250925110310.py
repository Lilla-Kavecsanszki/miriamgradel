from django.http import HttpResponse
import os

def robots_txt(request):
    # Pre-deploy: ENV is not "prod" → disallow crawling.
    is_prod = os.getenv("ENV", "dev").lower() == "prod"
    if is_prod:
        content = (
            "User-agent: *\n"
            "Allow: /\n"
            f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}\n"
        )
    else:
        content = "User-agent: *\nDisallow: /\n"
    return HttpResponse(content, content_type="text/plain")
