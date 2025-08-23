# journalism/models.py
from datetime import date
from django.utils import timezone
from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail import blocks

from behind_scenes.models import BTSPage


# ---------- WRITTEN (Index only) ----------

class WrittenIndexPage(Page):
    """
    Index page for Written work. No child detail pages.
    Editors add items via StreamField; links go out to external URLs.
    Also shows BTS teasers for the Written category.
    """
    template = "written_page.html"

    intro = RichTextField(blank=True)

    # Items live here instead of child pages
    articles = StreamField(
        [
            ("article", blocks.StructBlock([
                ("title", blocks.CharBlock(required=True)),
                ("publication_name", blocks.CharBlock(required=False)),
                ("publication_date", blocks.DateBlock(required=False)),
                ("external_url", blocks.URLBlock(required=True, help_text="Destination URL")),
                ("excerpt", blocks.TextBlock(required=False)),
            ])),
        ],
        use_json_field=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("articles"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = []  # <-- no detail pages under this

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)

        year = date.today().year

        # turn stream items into simple dicts
        items = []
        for blk in self.articles:
            if blk.block_type == "article":
                v = blk.value
                items.append(
                    {
                        "title": v.get("title"),
                        "publication_name": v.get("publication_name"),
                        "publication_date": v.get("publication_date"),
                        "external_url": v.get("external_url"),
                        "excerpt": v.get("excerpt"),
                    }
                )

        # sort by publication_date desc (missing dates sink)
        def pubdate(a):
            return a["publication_date"] or date.min

        items_sorted = sorted(items, key=pubdate, reverse=True)

        # split into current year vs previous
        recent, previous = [], []
        for a in items_sorted:
            y = (a["publication_date"] or date.min).year
            (recent if y == year else previous).append(a)

        # BTS teasers for Written
        bts_teasers = (
            BTSPage.objects.live()
            .filter(category="written")
            .order_by("-first_published_at")[:3]
        )

        ctx.update(
            {
                "current_year": year,
                "recent_articles": recent,
                "previous_articles": previous,
                "bts_teasers": bts_teasers,
            }
        )
        return ctx


# ---------- VIDEO (Index only) ----------

class VideoIndexPage(Page):
    """
    Index page for Videos. No child detail pages.
    Editors add items via StreamField; embeds + outbound links only.
    Also shows BTS teasers for the Video category.
    """
    template = "video_page.html"

    intro = RichTextField(blank=True)

    videos = StreamField(
        [
            ("video", blocks.StructBlock([
                ("title", blocks.CharBlock(required=True)),
                ("video_date", blocks.DateBlock(required=False)),
                ("embed_url", blocks.URLBlock(required=True, help_text="YouTube/Vimeo URL (oEmbed)")),
                ("standfirst", blocks.CharBlock(required=False, max_length=180)),
                ("description", blocks.RichTextBlock(required=False, features=["bold","italic","link","ol","ul"])),
                ("produced_by", blocks.CharBlock(required=False, max_length=120)),
                ("produced_for", blocks.CharBlock(required=False, max_length=120)),
                ("external_url", blocks.URLBlock(required=False, help_text="Optional link out (e.g., YouTube watch page)")),
            ])),
        ],
        use_json_field=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("videos"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = []  # <-- no detail pages under this

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)

        year = date.today().year

        # flatten stream into dicts
        vids = []
        for blk in self.videos:
            if blk.block_type == "video":
                v = blk.value
                vids.append(
                    {
                        "title": v.get("title"),
                        "video_date": v.get("video_date"),
                        "embed_url": v.get("embed_url"),
                        "standfirst": v.get("standfirst"),
                        "description": v.get("description"),
                        "produced_by": v.get("produced_by"),
                        "produced_for": v.get("produced_for"),
                        "external_url": v.get("external_url"),
                    }
                )

        # sort by effective date desc
        def pubdate(v):
            return v["video_date"] or date.min

        vids_sorted = sorted(vids, key=pubdate, reverse=True)

        featured = vids_sorted[0] if vids_sorted else None
        others = vids_sorted[1:] if len(vids_sorted) > 1 else []

        recent, previous = [], []
        for v in vids_sorted:
            (recent if (v["video_date"] or date.min).year == year else previous).append(v)

        # BTS teasers for Video
        bts_teasers = (
            BTSPage.objects.live()
            .filter(category="video")
            .order_by("-first_published_at")[:3]
        )

        ctx.update(
            {
                "current_year": year,
                "featured": featured,
                "videos": others,
                "recent_videos": recent,
                "previous_videos": previous,
                "bts_teasers": bts_teasers,
            }
        )
        return ctx


# ---------- AUDIO (Index/episodes already in template) ----------

class AudioPage(Page):
    """
    Audio index with episodes stored in a StreamField (you already render these).
    Adds BTS teasers for the Audio category.
    """
    template = "audio_page.html"

    intro = RichTextField(blank=True)

    # keep your existing structure if you already have it; included here for completeness
    episodes = StreamField(
        [
            ("episode", blocks.StructBlock([
                ("title", blocks.CharBlock(required=True)),
                ("date", blocks.DateBlock(required=False)),
                ("embed", blocks.RawHTMLBlock(required=True)),
                ("teaser", blocks.TextBlock(required=False)),
                ("behind_scenes", blocks.StructBlock([
                    ("page", blocks.PageChooserBlock(required=False, target_model="behind_scenes.BTSPage")),
                    ("label", blocks.CharBlock(required=False, default="Behind the Scenes")),
                ], required=False)),
            ])),
        ],
        use_json_field=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("episodes"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = []  # <-- no detail pages under this

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        ctx["bts_teasers"] = (
            BTSPage.objects.live()
            .filter(category="audio")
            .order_by("-first_published_at")[:3]
        )
        return ctx
