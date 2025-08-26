from django.db import models
from django.utils.html import strip_tags

from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock


# Categories used for grouping teasers
BTS_CATEGORIES = (
    ("written", "Written"),
    ("audio", "Audio"),
    ("video", "Video"),
    ("communication", "Communication"),
)


# -----------------------
# INDEX (intro + 3x grids)
# -----------------------
class BTSIndexPage(Page):
    """Landing page that shows intro + teaser cards grouped by category."""
    template = "bts_index_page.html"

    intro_heading = models.CharField(max_length=120, blank=True, default="Behind the Scenes")
    intro_body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro_heading"),
        FieldPanel("intro_body"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["behind_scenes.BTSPage"]  # <-- detail pages live under here

    def teasers_for_category(self, category: str, limit: int = 3):
        return (
            BTSPage.objects.child_of(self)
            .live()
            .filter(category=category)
            .order_by("-first_published_at")[:limit]
        )

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        ctx.update(
            {
                "written_teasers": self.teasers_for_category("written", 3),
                "audio_teasers": self.teasers_for_category("audio", 3),
                "video_teasers": self.teasers_for_category("video", 3),
            }
        )
        return ctx


# -----------------------
# DETAIL (one BTS item)
# -----------------------
class BTSPage(Page):
    """One BTS detail page with its own URL."""
    template = "bts_detail_page.html"

    # Category (controls where it appears as a teaser)
    category = models.CharField(
        max_length=20, choices=BTS_CATEGORIES, default="written",
        help_text="Which main section this BTS relates to.",
    )

    # Teaser card fields (used on index + sidebars)
    teaser_title = models.CharField(
        max_length=120, blank=True,
        help_text="Short title for teaser cards (falls back to page title).",
    )
    teaser_summary = models.CharField(
        max_length=220, blank=True,
        help_text="1–2 lines for teaser cards.",
    )
    teaser_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        help_text="Card/hero image.",
    )

    # Detail intro
    intro_title = models.CharField(
        max_length=120, blank=True,
        help_text="Optional heading on the detail page (falls back to page title).",
    )
    intro_body = RichTextField(blank=True, help_text="Intro paragraph under the heading.")

    # Rich detail body (paragraphs, images, embeds, gallery)
    body = StreamField(
        [
            ("paragraph", blocks.RichTextBlock(features=["h2", "h3", "bold", "italic", "link", "ol", "ul"])),
            ("image", blocks.StructBlock([
                ("image", ImageChooserBlock(required=True)),
                ("caption", blocks.CharBlock(required=False, max_length=200)),
                ("alignment", blocks.ChoiceBlock(
                    required=False,
                    choices=[("full", "Full width"), ("left", "Left"), ("right", "Right")],
                    default="full",
                )),
            ], icon="image", label="Image")),
            ("embed", EmbedBlock(help_text="YouTube/Vimeo/SoundCloud/Spotify, etc.")),
            ("gallery", blocks.StructBlock([
                ("items", blocks.ListBlock(
                    blocks.StructBlock([
                        ("image", ImageChooserBlock(required=True)),
                        ("caption", blocks.CharBlock(required=False, max_length=200)),
                    ], icon="image", label="Gallery image")
                )),
            ], icon="image", label="Gallery")),
        ],
        use_json_field=True, blank=True, null=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("category"),
        MultiFieldPanel(
            [FieldPanel("teaser_title"), FieldPanel("teaser_summary"), FieldPanel("teaser_image")],
            heading="Teaser card",
        ),
        MultiFieldPanel(
            [FieldPanel("intro_title"), FieldPanel("intro_body")],
            heading="Detail intro",
        ),
        FieldPanel("body"),
    ]

    parent_page_types = ["behind_scenes.BTSIndexPage"]  # <-- only under the index
    subpage_types = []  # no children

    # Helpers for cards/templates
    @property
    def card_title(self):
        return self.teaser_title or self.title

    @property
    def card_summary(self):
        if self.teaser_summary:
            return self.teaser_summary
        if self.intro_body:
            text = strip_tags(str(self.intro_body))
            return (text[:200] + "…") if len(text) > 200 else text
        return ""
