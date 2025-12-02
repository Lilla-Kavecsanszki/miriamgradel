import os


class AiOptOutMiddleware:
    """
    Adds AI opt-out headers to HTML responses in production.

    This sets:
        X-Robots-Tag: noai, noimageai
    which is used by some AI providers to respect training opt-outs.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Mirror your robots_txt logic: only treat ENV=prod as real production
        self.is_prod = os.getenv("ENV", "dev").lower() == "prod"

    def __call__(self, request):
        response = self.get_response(request)

        # Only apply in prod and only for HTML responses
        if self.is_prod and "text/html" in response.get("Content-Type", ""):
            existing = response.get("X-Robots-Tag", "")
            extra = "noai, noimageai"

            if existing:
                # Don't lose any existing value, just append
                response["X-Robots-Tag"] = f"{existing}, {extra}"
            else:
                response["X-Robots-Tag"] = extra

        return response
