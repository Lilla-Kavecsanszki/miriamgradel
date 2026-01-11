# behind_scenes/models.py
from __future__ import annotations

from django.db import models
from django.utils.html import strip_tags
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.embeds.blocks import EmbedBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page

# Categories used for grouping teasers
BTS_CATEGORIES = (
    ("written", "Written"),
    ("audio", "Audio"),
    ("video", "Video"),
    ("communication", "Communication"),
)


class BTSIndexPage(Page):
    """Landing page that shows intro + ALL teaser cards in one responsive grid."""

    template = "bts_index_page.html"

    intro_heading = models.CharField(
        max_length=120,
        blank=True,
        default="Behind the Scenes",
    )
    intro_body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro_heading"),
        FieldPanel("intro_body"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["behind_scenes.BTSPage"]  # detail pages live under here

    def teasers_for_category(self, category: str, limit: int = 3):
        """
        Optional helper: returns newest BTS items for a given category.
        Kept for compatibility if referenced elsewhere (e.g., sidebars).
        """
        return (
            BTSPage.objects.child_of(self)
            .live()
            .filter(category=category)
            .order_by("-first_published_at", "-latest_revision_created_at")
        )[:limit]

    def get_context(self, request, *args, **kwargs):
        """
        Provide a single combined queryset of all BTS items for the index page,
        ordered newest first. The template renders them in one Bootstrap grid
        (3 per row on lg, 2 on sm/md, 1 on xs).
        """
        ctx = super().get_context(request, *args, **kwargs)

        all_items = (
            BTSPage.objects.child_of(self)
            .live()
            .order_by("-first_published_at", "-latest_revision_created_at")
        )

        ctx.update(
            {
                "all_teasers": all_items,
                # Optional; keep if other templates still use them
                "written_teasers": self.teasers_for_category("written", 3),
                "audio_teasers": self.teasers_for_category("audio", 3),
                "video_teasers": self.teasers_for_category("video", 3),
                "communication_teasers": self.teasers_for_category(
                    "communication",
                    3,
                ),
            }
        )
        return ctx


class BTSPage(Page):
    """One BTS detail page with its own URL."""

    template = "bts_detail_page.html"

    category = models.CharField(
        max_length=20,
        choices=BTS_CATEGORIES,
        default="written",
        help_text="Which main section this BTS relates to.",
    )

    teaser_title = models.CharField(
        max_length=120,
        blank=True,
        help_text="Short title for teaser cards (falls back to page title).",
    )
    teaser_summary = models.CharField(
        max_length=220,
        blank=True,
        help_text="1–2 lines for teaser cards.",
    )
    teaser_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Card/hero image.",
    )

    intro_title = models.CharField(
        max_length=120,
        blank=True,
        help_text="Optional heading on the detail page (falls back to page title).",
    )
    intro_body = RichTextField(
        blank=True,
        help_text="Intro paragraph under the heading.",
    )

    body = StreamField(
        [
            (
                "paragraph",
                blocks.RichTextBlock(
                    features=["h2", "h3", "bold", "italic", "link", "ol", "ul"]
                ),
            ),
            (
                "image",
                blocks.StructBlock(
                    [
                        ("image", ImageChooserBlock(required=True)),
                        ("caption", blocks.CharBlock(required=False, max_length=200)),
                        (
                            "alignment",
                            blocks.ChoiceBlock(
                                required=False,
                                choices=[
                                    ("full", "Full width"),
                                    ("left", "Left"),
                                    ("right", "Right"),
                                ],
                                default="full",
                            ),
                        ),
                    ],
                    icon="image",
                    label="Image",
                ),
            ),
            ("embed", EmbedBlock(help_text="YouTube/Vimeo/SoundCloud/Spotify, etc.")),
            (
                "gallery",
                blocks.StructBlock(
                    [
                        (
                            "items",
                            blocks.ListBlock(
                                blocks.StructBlock(
                                    [
                                        ("image", ImageChooserBlock(required=True)),
                                        (
                                            "caption",
                                            blocks.CharBlock(
                                                required=False, max_length=200
                                            ),
                                        ),
                                    ],
                                    icon="image",
                                    label="Gallery image",
                                )
                            ),
                        ),
                    ],
                    icon="image",
                    label="Gallery",
                ),
            ),
        ],
        use_json_field=True,
        blank=True,
        # Prefer blank=True over null=True for JSON/content fields in Django.
        # Keeping NULL out of the DB avoids edge cases.
        null=False,
        default=list,
    )

    content_panels = Page.content_panels + [
        FieldPanel("category"),
        MultiFieldPanel(
            [
                FieldPanel("teaser_title"),
                FieldPanel("teaser_summary"),
                FieldPanel("teaser_image"),
            ],
            heading="Teaser card",
        ),
        MultiFieldPanel(
            [FieldPanel("intro_title"), FieldPanel("intro_body")],
            heading="Detail intro",
        ),
        FieldPanel("body"),
    ]

    parent_page_types = ["behind_scenes.BTSIndexPage"]
    subpage_types = []

    @property
    def card_title(self) -> str:
        return self.teaser_title or self.title

    @property
    def card_summary(self) -> str:
        """
        Prefer explicit teaser_summary; otherwise fall back to plain-text intro_body.
        """
        if self.teaser_summary:
            return self.teaser_summary

        if self.intro_body:
            # Convert RichText to plain text, normalize whitespace, then truncate.
            text = " ".join(strip_tags(str(self.intro_body)).split())
            if len(text) > 200:
                return f"{text[:200]}…"
            return text

        return ""
