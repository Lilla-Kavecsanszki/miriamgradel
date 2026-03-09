# journalism/models.py
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, List

from django.db import models
from django.utils import timezone
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page

if TYPE_CHECKING:
    # Only for type hints; doesn't import at runtime (avoids hard coupling)
    from behind_scenes.models import BTSPage  # noqa: F401


def get_bts_teasers(limit: int = 3) -> List["BTSPage"]:
    """
    Safely fetch latest BTS teasers without hard dependency on the app.

    - No blanket exception swallowing.
    - No migrations (pure Python change).
    - Returns [] if behind_scenes app isn't installed or BTSPage can't be imported.
    """
    try:
        from behind_scenes.models import BTSPage
    except ImportError:
        return []

    return list(
        BTSPage.objects.live()
        .specific()
        .order_by("-first_published_at")[:limit]
    )


# ======================
# WRITTEN
# ======================


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

    qs = list(self.articles.all())

    def pubdate(item):
        if item.publication_date:
            return item.publication_date
        # stable fallback even if missing date
        if self.first_published_at:
            return timezone.localtime(self.first_published_at).date()
        return date.min

    items = sorted(qs, key=pubdate, reverse=True)

    ctx.update(
        {
            "recent_articles": items[:3],     # newest 3
            "previous_articles": items[3:],   # the rest
            "bts_teasers": get_bts_teasers(limit=3),
        }
    )
    return ctx


class WrittenArticleItem(Orderable):
    page = ParentalKey(WrittenPage, related_name="articles", on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    publication_name = models.CharField(
        max_length=150, blank=True, help_text="e.g. The Sun"
    )
    publication_date = models.DateField(null=True, blank=True)
    external_url = models.URLField(
        blank=True, help_text="If set, the index links out to this URL."
    )
    excerpt = models.TextField(blank=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("publication_name"),
        FieldPanel("publication_date"),
        FieldPanel("external_url"),
        FieldPanel("excerpt"),
    ]


# ======================
# VIDEO
# ======================


class VideoPage(Page):
    """
    Holds video items (no child pages).
    Renders a featured video (newest by date) plus lists/buckets.
    """

    template = "video_page.html"
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        MultiFieldPanel([InlinePanel("videos", label="Video")], heading="Videos"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = []

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)

        year = date.today().year
        qs = list(self.videos.all())

        def pubdate(item):
            if item.video_date:
                return item.video_date
            if self.first_published_at:
                return timezone.localtime(self.first_published_at).date()
            return date.min

        videos_sorted = sorted(qs, key=pubdate, reverse=True)

        featured = videos_sorted[0] if videos_sorted else None
        others = videos_sorted[1:] if len(videos_sorted) > 1 else []

        recent: list[VideoItem] = []
        previous: list[VideoItem] = []
        for video in videos_sorted:
            (recent if pubdate(video).year == year else previous).append(video)

        ctx.update(
            {
                "current_year": year,
                "featured": featured,
                "videos": others,  # flat list for “All my videos”
                "recent_videos": recent,
                "previous_videos": previous,
            }
        )
        return ctx


class VideoItem(Orderable):
    """
    One video row that lives inside a VideoPage.
    If 'external_url' is set, index links out.
    """

    page = ParentalKey(VideoPage, related_name="videos", on_delete=models.CASCADE)

    video_date = models.DateField(null=True, blank=True)
    standfirst = models.CharField(max_length=180, blank=True)
    description = RichTextField(
        features=["bold", "italic", "link", "ol", "ul"], blank=True
    )

    embed_url = models.URLField(help_text="YouTube/Vimeo URL (oEmbed).")

    produced_by = models.CharField(max_length=120, blank=True)
    produced_for = models.CharField(max_length=120, blank=True)

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
        ordering = ["-video_date", "-id"]

    def __str__(self):
        label = self.standfirst or (self.produced_for or "Untitled")
        when = self.video_date.isoformat() if self.video_date else "No date"
        return f"{label} — {when}"


# ======================
# AUDIO
# ======================


class AudioPage(Page):
    """
    Holds audio items; renders a featured player (newest by date) and a list.
    """

    template = "audio_page.html"
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        MultiFieldPanel([InlinePanel("audios", label="Audio")], heading="Audio items"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = []

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)

        year = date.today().year
        items = list(self.audios.all())

        def pubdate(item):
            if item.audio_date:
                return item.audio_date
            if self.first_published_at:
                return timezone.localtime(self.first_published_at).date()
            return date.min

        audios_sorted = sorted(items, key=pubdate, reverse=True)

        featured = audios_sorted[0] if audios_sorted else None
        others = audios_sorted[1:] if len(audios_sorted) > 1 else []

        recent: list[AudioItem] = []
        previous: list[AudioItem] = []
        for item in audios_sorted:
            (recent if pubdate(item).year == year else previous).append(item)

        ctx.update(
            {
                "current_year": year,
                "featured": featured,
                "audios": others,  # flat list for “All my audio”
                "recent_audios": recent,
                "previous_audios": previous,
                "bts_teasers": get_bts_teasers(limit=3),
            }
        )
        return ctx


class AudioItem(Orderable):
    """
    One audio row inside AudioPage.
    Use oEmbed-able URLs (SoundCloud, Spotify, etc.) in `embed_url`.
    """

    page = ParentalKey(AudioPage, related_name="audios", on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    audio_date = models.DateField(null=True, blank=True)
    standfirst = models.CharField(max_length=180, blank=True)
    description = RichTextField(
        features=["bold", "italic", "link", "ol", "ul"], blank=True
    )

    embed_url = models.URLField(help_text="SoundCloud/Spotify/etc. URL (oEmbed).")

    produced_by = models.CharField(max_length=120, blank=True)
    produced_for = models.CharField(max_length=120, blank=True)

    external_url = models.URLField(
        blank=True, help_text="If set, buttons link out to this URL."
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("audio_date"),
        FieldPanel("standfirst"),
        FieldPanel("embed_url"),
        FieldPanel("description"),
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
        ordering = ["-audio_date", "-id"]

    def __str__(self):
        when = self.audio_date.isoformat() if self.audio_date else "No date"
        return f"{self.title} — {when}"
