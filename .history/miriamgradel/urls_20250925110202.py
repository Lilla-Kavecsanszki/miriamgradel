from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views

from .views import robots_txt  # see views.py below

urlpatterns = [
    # Django & Wagtail admin (not localized)
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),

    # Wagtail documents app (not localized)
    path("documents/", include(wagtaildocs_urls)),

    # Project routes
    path("search/", search_views.search, name="search"),

    # i18n helpers & SEO endpoints
    path("django-i18n/", include("django.conf.urls.i18n")),  # POST to change language (optional UI)
    path("sitemap.xml", sitemap),                            # auto-generated sitemap
    path("robots.txt", robots_txt),                          # env-aware robots
]

# Wagtail page serving inside i18n-aware patterns.
# Default language has no /en/ prefix; translated pages will be /da/... and /ja/...
urlpatterns += i18n_patterns(
    path("", include(wagtail_urls)),
    prefix_default_language=False,
)

# Static / media in development only
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
