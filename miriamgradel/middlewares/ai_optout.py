from django.conf import settings


class AiOptOutMiddleware:
    """
    Adds AI opt-out headers to HTML responses in non-DEBUG environments.

    Sets:
        X-Robots-Tag: noai, noimageai
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only apply when not DEBUG and only for HTML responses
        if not settings.DEBUG and "text/html" in response.get("Content-Type", ""):
            existing = response.get("X-Robots-Tag", "")
            extra = "noai, noimageai"

            if existing:
                response["X-Robots-Tag"] = f"{existing}, {extra}"
            else:
                response["X-Robots-Tag"] = extra

        return response
