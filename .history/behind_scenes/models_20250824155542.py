# behind_scenes/models.py
from django.db import models
from django.utils.html import strip_tags

from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


# --- constants / helpers ---

BTS_CATEGORIES = (
    ("written", "Written"),
    ("audio", "Audio"),
    ("video", "Video"),
)


class BTSSliceBlock(blocks.StructBlock):
    """
    A single 'Behind the Scenes' section:
    - subtitle
    - body rich text
    - optional image (with simple left/right/full layout)
    """
    subtitle = blocks.CharBlock(required=True, max_length=150, help_text="Section subtitle")
    body = blocks.RichTextBlock(required=True, help_text="Paragraph text")
    image = ImageChooserBlock(required=False, help_text="Optional supporting image")
    image_position = blocks.ChoiceBlock(
        required=False,
        choices=[("left", "Image left"), ("right", "Image right"), ("full", "Image full width")],
        default="right",
        help_text="How to place the image relative to the text",
    )
    anchor = blocks.CharBlock(required=False, help_text="Optional anchor id (e.g., 'research-ethics')")

    class Meta:
        icon = "doc-full"
        label = "Behind-the-scenes section"


class BTSIndexPage(Page):
    """
    Landing page for all BTS content.
    Shows SHORT teasers: 2–3 per category (Written/Audio/Video),
    and each card links to a BTS detail page.
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
    Single 'Behind the Scenes' explanation page (detail).
    Independent from Written/Audio/Video models.
    """
    template = "bts_detail_page.html"

    # categorisation so index can group by category
    category = models.CharField(
        max_length=20,
        choices=BTS_CATEGORIES,
        default="written",
        help_text="Which main category this BTS relates to.",
    )

    # page intro
    intro_title = models.CharField(
        max_length=120,
        default="Full Transparency",
        help_text="Main heading shown above the intro",
    )
    intro_body = RichTextField(
        blank=True,
        help_text="Introductory paragraph under the heading",
    )

    # teaser fields for cards
    teaser_title = models.CharField(
        max_length=120,
        blank=True,
        help_text="Optional short title for teaser cards. Falls back to page title.",
    )
    teaser_summary = models.CharField(
        max_length=220,
        blank=True,
        help_text="1–2 lines max shown on cards. If empty, a truncation of the intro/body is used.",
    )
    teaser_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional image for teaser cards.",
    )

    # main structured content
    slices = StreamField(
        [("section", BTSSliceBlock())],
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
            heading="Intro",
        ),
        MultiFieldPanel(
            [
                FieldPanel("teaser_title"),
                FieldPanel("teaser_summary"),
                FieldPanel("teaser_image"),
            ],
            heading="Teaser (for cards)",
        ),
        FieldPanel("slices"),
    ]

    parent_page_types = ["behind_scenes.BTSIndexPage"]
    subpage_types = []

    # --- convenience for templates ---

    @property
    def card_title(self):
        return self.teaser_title or self.title

    @property
    def card_summary(self):
        if self.teaser_summary:
            return self.teaser_summary
        # fallback: try intro, else first slice's body, else empty
        if self.intro_body:
            intro_text = strip_tags(str(self.intro_body))
            return (intro_text[:200] + "…") if len(intro_text) > 200 else intro_text
        if self.slices:
            for block in self.slices:
                if block.block_type == "section":
                    body = block.value.get("body")
                    if body:
                        text = strip_tags(getattr(body, "source", str(body)))
                        return (text[:200] + "…") if len(text) > 200 else text
        return ""

    @property
    def teaser_sections(self):
        """
        Return sections that have anchors — handy for an in-page TOC.
        """
        teasers = []
        if self.slices:
            for block in self.slices:
                if block.block_type == "section":
                    val = block.value
                    if val.get("anchor"):
                        body = val.get("body")
                        text = strip_tags(getattr(body, "source", str(body)))
                        teasers.append(
                            {
                                "anchor": val.get("anchor"),
                                "subtitle": val.get("subtitle"),
                                "image": val.get("image"),
                                "teaser_text": (text[:180] + "…") if len(text) > 180 else text,
                            }
                        )
        return teasers
