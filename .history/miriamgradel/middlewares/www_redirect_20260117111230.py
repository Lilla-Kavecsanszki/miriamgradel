from django.http import HttpResponsePermanentRedirect


class WwwRedirectMiddleware:
    """
    301 redirect www.miriamgradel.cc -> miriamgradel.cc (preserves path + querystring).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()  # may include port
        if host.startswith("www."):
            new_host = host[4:]
            scheme = "https" if request.is_secure() else "http"
            return HttpResponsePermanentRedirect(f"{scheme}://{new_host}{request.get_full_path()}")
        return self.get_response(request)
