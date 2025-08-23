# models.py (snippet)

from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from modelcluster.fields import ParentalKey

class WrittenPage(Page):
    template = "written_page.html"
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        MultiFieldPanel([InlinePanel("articles", label="Article")], heading="Articles"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = []

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        from datetime import date
        from django.utils import timezone

        year = date.today().year
        qs = list(self.articles.all())

        def pubdate(it):
            if it.publication_date:
                return it.publication_date
            # fallback so sort is stable even if missing date
            return (self.first_published_at and timezone.localtime(self.first_published_at).date()) or date.min

        items = sorted(qs, key=pubdate, reverse=True)
        recent, previous = [], []
        for it in items:
            (recent if pubdate(it).year == year else previous).append(it)

        # BTS teasers -> match your template variable name
        bts_teasers = []
        try:
            from bts.models import BTSPage  # adjust path to where BTSPage lives
            bts_teasers = BTSPage.objects.live().specific().order_by("-first_published_at")[:3]
        except Exception:
            pass

        ctx.update(
            {
                "current_year": year,
                "recent_articles": recent,
                "previous_articles": previous,
                "bts_teasers": bts_teasers,
            }
        )
        return ctx


class WrittenArticleItem(Orderable):
    page = ParentalKey(WrittenPage, related_name="articles", on_delete=models.CASCADE)

    title = models.CharField(max_length=200)  # <— add this
    publication_name = models.CharField(max_length=150, blank=True, help_text="e.g. The Sun")
    publication_date = models.DateField(null=True, blank=True)
    external_url = models.URLField(blank=True, help_text="If set, the index links out to this URL.")
    excerpt = models.TextField(blank=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("publication_name"),
        FieldPanel("publication_date"),
        FieldPanel("external_url"),
        FieldPanel("excerpt"),
    ]




# VIDEO
class VideoPage(Page):
    """
    Holds video items (no child pages).
    Renders a featured video (newest by date) plus lists/buckets.
    """
    template = "video_page.html"

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        MultiFieldPanel(
            [
                InlinePanel("videos", label="Video"),
            ],
            heading="Videos",
        ),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = []  # nothing underneath

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)

        year = date.today().year
        qs = self.videos.all()

        # prefer explicit video_date if present
        def pubdate(item):
            if item.video_date:
                return item.video_date
            # fall back to this page's first_published_at (so ordering is stable even if no dates set)
            if self.first_published_at:
                return timezone.localtime(self.first_published_at).date()
            return date.min

        videos_sorted = sorted(qs, key=pubdate, reverse=True)

        featured = videos_sorted[0] if videos_sorted else None
        others = videos_sorted[1:] if len(videos_sorted) > 1 else []

        # Buckets by year (for “My last video in {{year}}” + archive)
        recent, previous = [], []
        for v in videos_sorted:
            (recent if pubdate(v).year == year else previous).append(v)

        ctx.update(
            {
                "current_year": year,
                "featured": featured,
                "videos": others,           # flat list for “All my videos”
                "recent_videos": recent,    # optional “this year” group
                "previous_videos": previous,
            }
        )
        return ctx


class VideoItem(Orderable):
    """
    One video row that lives *inside* a VideoPage.
    If 'external_url' is set, index links out; else we can show the embed on the index.
    """
    page = ParentalKey(VideoPage, related_name="videos", on_delete=models.CASCADE)

    # Display/meta
    video_date = models.DateField(null=True, blank=True)
    standfirst = models.CharField(max_length=180, blank=True)
    description = RichTextField(features=["bold", "italic", "link", "ol", "ul"], blank=True)

    # Media
    embed_url = models.URLField(help_text="YouTube/Vimeo URL (oEmbed).")

    # Credits
    produced_by = models.CharField(max_length=120, blank=True)
    produced_for = models.CharField(max_length=120, blank=True)

    # Optional external destination (e.g., YouTube watch page)
    external_url = models.URLField(blank=True, help_text="If set, index links out.")

    panels = [
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
            ],
            heading="Credits & Links",
        ),
    ]

    class Meta(Orderable.Meta):
        ordering = ["-video_date", "-id"]  # server-side default

    def __str__(self):
        label = self.standfirst or (self.produced_for or "Untitled")
        when = self.video_date.isoformat() if self.video_date else "No date"
        return f"{label} — {when}"