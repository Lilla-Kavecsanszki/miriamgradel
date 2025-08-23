from datetime import date
from django.utils import timezone
from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel

from modelcluster.fields import ParentalKey
from wagtail.models import Orderable


from behind_scenes.models import BTSPage

class WrittenPage(Page):
    """
    Holds article items (no child pages) and shows a BTS sidebar.
    """
    template = "written_page.html"

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        MultiFieldPanel(
            [
                InlinePanel("articles", label="Articles"),
            ],
            heading="Articles",
        ),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = []  # Nothing underneath

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)

        year = date.today().year

        # Base queryset of article items (not pages)
        qs = self.articles.all()

        # Helper: prefer publication_date, else fallback to this page's first_published_at.date()
        def pubdate(item):
            if item.publication_date:
                return item.publication_date
            if self.first_published_at:
                return timezone.localtime(self.first_published_at).date()
            return date.min

        # Sort and bucket like before
        items = sorted(qs, key=pubdate, reverse=True)
        recent, previous = [], []
        for it in items:
            (recent if pubdate(it).year == year else previous).append(it)

        # Example: latest BTS items if you have a BTSPage model (leave as-is or remove if not used)
        bts_qs = []
        try:
            from .models import BTSPage  # adjust import to wherever BTSPage lives
            bts_qs = BTSPage.objects.live().specific().order_by("-first_published_at")[:3]
        except Exception:
            pass

        ctx.update(
            {
                "current_year": year,
                "recent_articles": recent,
                "previous_articles": previous,
                "bts_items": bts_qs,
            }
        )
        return ctx


class WrittenArticleItem(Orderable):
    """
    One article row that lives *inside* a WrittenPage.
    If 'external_url' is set, the index links to it; otherwise we can render plain text.
    """
    page = ParentalKey(WrittenPage, on_delete=models.CASCADE, related_name="articles")

    publication_name = models.CharField(
        max_length=150, blank=True, help_text="e.g. The Sun"
    )
    publication_date = models.DateField(null=True, blank=True)
    external_url = models.URLField(
        blank=True, help_text="If set, the index links out to this URL."
    )
    excerpt = models.TextField(blank=True)

    panels = [
        FieldPanel("publication_name"),
        FieldPanel("publication_date"),
        FieldPanel("external_url"),
        FieldPanel("excerpt"),
    ]

    class Meta(Orderable.Meta):
        # Optional: default ordering newest first if you skip the Python-side sort
        ordering = ["-publication_date", "-id"]

    def __str__(self):
        return f"{self.publication_name or 'Untitled'} — {self.publication_date or 'No date'}"



# --- VIDEO ---

class VideoPage(Page):
    """
    Lists VideoPage children (latest featured on top)
    """
    template = "video_page.html"

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    parent_page_types = ["home.HomePage"]

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
