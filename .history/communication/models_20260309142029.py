# communication/models.py
from __future__ import annotations

from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page


class ExampleItemBlock(blocks.StructBlock):
    """A project highlight card (for the highlights row)."""

    title = blocks.CharBlock(required=False, max_length=120)
    description = blocks.TextBlock(required=False)
    image = ImageChooserBlock(required=False)
    link_label = blocks.CharBlock(required=False, max_length=80)
    link_url = blocks.URLBlock(required=False)

    class Meta:
        label = "Example / Project"
        icon = "snippet"


class InstagramCardBlock(blocks.StructBlock):
    """Instagram preview card with image + link."""

    url = blocks.URLBlock(
        required=True,
        help_text="Paste the clean Instagram post or reel URL.",
    )
    preview_image = ImageChooserBlock(
        required=True,
        help_text="Upload a preview image or screenshot for the Instagram post.",
    )
    title = blocks.CharBlock(
        required=False,
        max_length=120,
        help_text="Optional short title shown under the preview.",
    )

    class Meta:
        label = "Instagram card"
        icon = "image"


class ServiceCardBlock(blocks.StructBlock):
    """
    One service offering.
    All main content areas (Description, Offering, Example, Output) are rich text.
    """

    slug = blocks.CharBlock(
        required=False,
        help_text=(
            "Optional anchor id (e.g. 'event-planning'). "
            "If left blank, the title will be slugified."
        ),
    )

    title = blocks.CharBlock(
        required=False,
        max_length=120,
        help_text="Service offering title (optional).",
    )

    details = blocks.RichTextBlock(
        required=True,
        help_text="Service description / background.",
    )

    offering = blocks.RichTextBlock(
        required=False,
        help_text="What you offer under this service.",
    )

    image = ImageChooserBlock(
        required=False,
        help_text="Image for this service (shown under the Offering section).",
    )

    example = blocks.RichTextBlock(
        required=False,
        help_text="Example or case description for this service.",
    )

    output = blocks.RichTextBlock(
        required=False,
        help_text="Outputs / results you deliver; can include bullet lists.",
    )

    class Meta:
        label = "Service card"
        icon = "cog"


class CommunicationPage(Page):
    """
    A single Communication page with intro text, service cards, optional highlights,
    and optional social media cards (Instagram, YouTube, etc.).
    """

    template = "communication.html"

    intro = RichTextField(blank=True, help_text="Optional introductory text.")

    services = StreamField(
        [("service", ServiceCardBlock())],
        blank=True,
        null=True,  # keep: avoids DB/schema change
        use_json_field=True,
        help_text="Add, remove, or reorder services.",
    )

    project_highlights = StreamField(
        [("highlight", ExampleItemBlock())],
        blank=True,
        null=True,  # keep: avoids DB/schema change
        use_json_field=True,
        help_text="Optional highlights row at the end (e.g. Techfestival, OpenNext).",
    )

    instagram_reels = StreamField(
        [("instagram_card", InstagramCardBlock())],
        blank=True,
        null=True,
        use_json_field=True,
        help_text="Optional Instagram cards shown at the bottom.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("services"),
        FieldPanel("project_highlights"),
        FieldPanel("instagram_reels"),
    ]
