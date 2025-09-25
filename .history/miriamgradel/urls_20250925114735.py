from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns

# ✅ Import Wagtail's SITEMAP VIEW with an alias
from wagtail.contrib.sitemaps.views import sitemap as wagtail_sitemap
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views
from .views import robots_txt

urlpatterns = [
    # Admins (not localized)
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),

    # Project routes
    path("search/", search_views.search, name="search"),

    # i18n helper (optional)
    path("django-i18n/", include("django.conf.urls.i18n")),

    # SEO endpoints
    path("sitemap.xml", wagtail_sitemap),   # ✅ Wagtail auto sitemap
    path("robots.txt", robots_txt),
]

# Wagtail page serving (i18n-aware). Default lang has no /en/.
urlpatterns += i18n_patterns(
    path("", include(wagtail_urls)),
    prefix_default_language=False,
)

# Static / media in development only
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
