from datetime import date
from django.utils import timezone
from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from modelcluster.fields import ParentalManyToManyField


class WrittenPage(Page):
    """
    Lists WrittenArticlePage children and shows a BTS sidebar.
    """
    template = "written_page.html"

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    parent_page_types = ["home.HomePage"]

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

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("publication_name"),
                FieldPanel("publication_date"),
                FieldPanel("external_url"),
                FieldPanel("excerpt"),
            ],
            heading="Article info",
        ),
    ]

    parent_page_types = ["journalism.WrittenIndexPage"]
    subpage_types = []


# --- VIDEO ---

class VideoIndexPage(Page):
    """
    Lists VideoPage children (latest featured on top)
    """
    template = "video_index_page.html"

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["journalism.VideoPage"]

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)

        year = date.today().year

        qs = (
            self.get_children()
            .live()
            .specific()
            .order_by("-first_published_at", "-latest_revision_created_at")
        )

        # prefer explicit video_date if present
        def pubdate(p):
            if getattr(p, "video_date", None):
                return p.video_date
            if p.first_published_at:
                return timezone.localtime(p.first_published_at).date()
            return date.min

        videos_sorted = sorted(qs, key=pubdate, reverse=True)

        featured = videos_sorted[0] if videos_sorted else None
        others = videos_sorted[1:] if videos_sorted[1:] else []

        # Buckets by year (for “My last video in {{year}}” + archive feel)
        recent, previous = [], []
        for v in videos_sorted:
            (recent if pubdate(v).year == year else previous).append(v)

        ctx.update(
            {
                "current_year": year,
                "featured": featured,
                "videos": others,           # flat list for “All my videos”
                "recent_videos": recent,    # if you want a “this year” group
                "previous_videos": previous,
            }
        )
        return ctx


class VideoPage(Page):
    """
    Single video. If external_url is set, index links out; else to this page.
    """
    template = "video_page.html"

    # Display/meta
    video_date = models.DateField(null=True, blank=True)
    standfirst = models.CharField(max_length=180, blank=True)
    description = RichTextField(features=["bold", "italic", "link", "ol", "ul"], blank=True)

    # Media
    embed_url = models.URLField(help_text="YouTube/Vimeo URL (oEmbed).")

    # Credits (as in your mock)
    produced_by = models.CharField(max_length=120, blank=True)
    produced_for = models.CharField(max_length=120, blank=True)

    # Optional external destination (e.g., YouTube watch page)
    external_url = models.URLField(blank=True, help_text="If set, index links out.")

    # Optional BTS relation to reuse your sidebar pattern
    related_bts = ParentalManyToManyField(
        "behind_scenes.BTSPage", blank=True, related_name="related_videos"
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("video_date"),
                FieldPanel("standfirst"),
                FieldPanel("embed_url"),
                FieldPanel("description"),
            ],
            heading="Video",
        ),
        MultiFieldPanel(
            [
                FieldPanel("produced_by"),
                FieldPanel("produced_for"),
                FieldPanel("external_url"),
                FieldPanel("related_bts"),
            ],
            heading="Credits & Links",
        ),
    ]

    parent_page_types = ["journalism.VideoIndexPage"]
    subpage_types = []
