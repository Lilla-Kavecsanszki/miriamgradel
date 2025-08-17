from datetime import date
from django.utils import timezone
from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from modelcluster.fields import ParentalManyToManyField

from behind_scenes.models import BTSPage


class WrittenIndexPage(Page):
    """
    Lists WrittenArticlePage children and shows a BTS sidebar.
    """
    template = "written_index_page.html"

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["journalism.WrittenArticlePage"]

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)

        year = date.today().year

        # Base queryset of child articles
        qs = (
            self.get_children()
            .live()
            .specific()
            .order_by("-first_published_at", "-latest_revision_created_at")
        )

        # Helper: prefer publication_date, else first_published_at.date()
        def pubdate(p):
            if getattr(p, "publication_date", None):
                return p.publication_date
            if p.first_published_at:
                return timezone.localtime(p.first_published_at).date()
            return date.min  # very old so it sinks to bottom

        # Sort by our effective pub date (desc) and split into buckets
        articles = sorted(qs, key=pubdate, reverse=True)
        recent, previous = [], []
        for a in articles:
            (recent if pubdate(a).year == year else previous).append(a)

        ctx.update(
            {
                "current_year": year,
                "recent_articles": recent,
                "previous_articles": previous,
                "bts_items": BTSPage.objects.live().specific().order_by(
                    "-first_published_at"
                )[:3],
            }
        )
        return ctx


class WrittenArticlePage(Page):
    """
    A single article. If 'external_url' is set, the index links to it;
    otherwise it links to this page detail.
    """
    template = "written_article_page.html"

    publication_name = models.CharField(
        max_length=150, blank=True, help_text="e.g. The Sun"
    )
    publication_date = models.DateField(null=True, blank=True)
    external_url = models.URLField(
        blank=True, help_text="If set, the index links out to this URL."
    )
    excerpt = models.TextField(blank=True)

    related_bts = ParentalManyToManyField(
        "behind_scenes.BTSPage", blank=True, related_name="related_articles"
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("publication_name"),
                FieldPanel("publication_date"),
                FieldPanel("external_url"),
                FieldPanel("excerpt"),
                FieldPanel("related_bts"),
            ],
            heading="Article info",
        ),
    ]

    parent_page_types = ["journalism.WrittenIndexPage"]
    subpage_types = []
