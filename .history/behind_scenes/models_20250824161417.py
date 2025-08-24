from django.db import models
from django.utils.html import strip_tags

from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

# --- constants ---

BTS_CATEGORIES = (
    ("written", "Written"),
    ("audio", "Audio"),
    ("video", "Video"),
)

# --- content blocks for BTS detail ---

class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    caption = blocks.CharBlock(required=False, max_length=200)
    alignment = blocks.ChoiceBlock(
        required=False,
        choices=[("full", "Full width"), ("left", "Left"), ("right", "Right")],
        default="full",
    )

    class Meta:
        icon = "image"
        label = "Image"

class GalleryBlock(blocks.StructBlock):
    items = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("image", ImageChooserBlock(required=True)),
                ("caption", blocks.CharBlock(required=False, max_length=200)),
            ],
            icon="image",
            label="Gallery image",
        ),
        help_text="Add multiple images with optional captions.",
    )

    class Meta:
        icon = "image"
        label = "Gallery"

# --- pages ---

class BTSIndexPage(Page):
    """
    Landing page for all BTS content.
    Shows teaser cards grouped by category.
    """
    template = "bts_index_page.html"

    intro_heading = models.CharField(max_length=120, blank=True, default="Behind the Scenes")
    intro_body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro_heading"),
        FieldPanel("intro_body"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["behind_scenes.BTSPage"]

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
                "written_teasers": self.teasers_for_category("written", limit=3),
                "audio_teasers": self.teasers_for_category("audio", limit=3),
                "video_teasers": self.teasers_for_category("video", limit=3),
            }
        )
        return ctx


class BTSPage(Page):
    """
    Single Behind-the-Scenes item.
    - Editors choose category (Written/Audio/Video)
    - Card fields power the index and sidebars
    - Body StreamField powers the detail page (paragraphs, images, embeds, galleries)
    """
    template = "bts_detail_page.html"

    # Category used for grouping / filtering in other sections
    category = models.CharField(
        max_length=20,
        choices=BTS_CATEGORIES,
        default="written",
        help_text="Which main category this BTS relates to (controls where teasers appear).",
    )

    # Intro on the detail page
    intro_title = models.CharField(
        max_length=120,
        blank=True,
        help_text="Optional heading shown on the detail page (falls back to page title).",
    )
    intro_body = RichTextField(
        blank=True,
        help_text="Intro paragraph shown under the heading on the detail page.",
    )

    # Teaser card fields (used on index and elsewhere)
    teaser_title = models.CharField(
        max_length=120,
        blank=True,
        help_text="Short title for teaser cards (falls back to page title).",
    )
    teaser_summary = models.CharField(
        max_length=220,
        blank=True,
        help_text="1–2 line summary for teaser cards.",
    )
    teaser_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Card/hero image for this BTS item.",
    )

    # Detail content (rich)
    body = StreamField(
        [
            ("paragraph", blocks.RichTextBlock(features=["h2", "h3", "bold", "italic", "link", "ol", "ul"])),
            ("image", ImageBlock()),
            ("embed", EmbedBlock(help_text="YouTube/Vimeo/SoundCloud/Spotify, etc.")),
            ("gallery", GalleryBlock()),
        ],
        use_json_field=True,
        blank=True,
        null=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("category"),
        MultiFieldPanel(
            [
                FieldPanel("intro_title"),
                FieldPanel("intro_body"),
            ],
            heading="Detail intro",
        ),
        MultiFieldPanel(
            [
                FieldPanel("teaser_title"),
                FieldPanel("teaser_summary"),
                FieldPanel("teaser_image"),
            ],
            heading="Teaser card",
        ),
        FieldPanel("body"),
    ]

    parent_page_types = ["behind_scenes.BTSIndexPage"]
    subpage_types = []

    # --- helpers for templates ---

    @property
    def card_title(self):
        return self.teaser_title or self.title

    @property
    def card_summary(self):
        if self.teaser_summary:
            return self.teaser_summary
        if self.intro_body:
            t = strip_tags(str(self.intro_body))
            return (t[:200] + "…") if len(t) > 200 else t
        return ""
