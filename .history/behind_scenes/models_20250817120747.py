from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

# behind_scenes/models.py

from django.utils.html import strip_tags

class BTSPage(Page):
    template = "bts_page.html"
    intro_title = models.CharField(max_length=120, default="Full Transparency")
    intro_body = RichTextField(blank=True)

    slices = StreamField([("section", BTSSliceBlock())],
                         use_json_field=True, blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro_title"),
        FieldPanel("intro_body"),
        FieldPanel("slices"),
    ]

    @property
    def teaser_image(self):
        """
        Return the first image found in the slices (if any).
        """
        if self.slices:
            for block in self.slices:
                if block.block_type == "section":
                    img = block.value.get("image")
                    if img:
                        return img
        return None

    @property
    def teaser_text(self):
        """
        Prefer intro_body; otherwise the first section body (as plain text).
        """
        if self.intro_body:
            return strip_tags(self.intro_body)  # plain text for sidebar
        if self.slices:
            for block in self.slices:
                if block.block_type == "section":
                    body = block.value.get("body")
                    if body:
                        return strip_tags(body.source if hasattr(body, "source") else str(body))
        return ""

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
