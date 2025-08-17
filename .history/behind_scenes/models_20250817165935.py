from django.db import models
from django.utils.html import strip_tags
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class BTSSliceBlock(blocks.StructBlock):
    """
    A single 'Behind the Scenes' section:
    - subtitle
    - body rich text
    - optional image (with simple left/right layout choice)
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


class BTSPage(Page):
    """
    Single 'Behind the Scenes' explanation page.
    """
    template = "bts_page.html"

    intro_title = models.CharField(
        max_length=120,
        default="Full Transparency",
        help_text="Main heading shown above the intro",
    )
    intro_body = RichTextField(
        blank=True,
        help_text="Introductory paragraph under the heading",
    )

    slices = StreamField(
        [("section", BTSSliceBlock())],
        use_json_field=True,
        blank=True,
        null=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro_title"),
        FieldPanel("intro_body"),
        FieldPanel("slices"),
    ]

    @property
    def teaser_sections(self):
        """
        Return a list of dicts for each section that has an anchor.
        Used for rendering teasers/cards.
        """
        teasers = []
        if self.slices:
            for block in self.slices:
                if block.block_type == "section":
                    val = block.value
                    if val.get("anchor"):  # only sections with anchors
                        teasers.append({
                            "anchor": val.get("anchor"),
                            "subtitle": val.get("subtitle"),
                            "image": val.get("image"),
                            "teaser_text": strip_tags(
                                val.get("body").source
                                if hasattr(val.get("body"), "source")
                                else str(val.get("body"))
                            )[:180] + "…",  # truncate nicely
                        })
        return teasers