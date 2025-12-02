from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page


# A simple block representing an example or project highlight (for the highlights row).
class ExampleItemBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, max_length=120)
    description = blocks.TextBlock(required=False)
    image = ImageChooserBlock(required=False)
    link_label = blocks.CharBlock(required=False, max_length=80)
    link_url = blocks.URLBlock(required=False)

    class Meta:
        label = "Example / Project"
        icon = "snippet"


class VideoEmbedBlock(blocks.StructBlock):
    embed_code = blocks.TextBlock(
        required=True,
        help_text=(
            "Paste any embed code (iframe, blockquote, script) OR a direct URL "
            "(Instagram / YouTube / Vimeo / TikTok, etc.)."
        ),
    )

    class Meta:
        label = "Video embed"
        icon = "media"


# One service offering.
# All main content areas (Description, Offering, Example, Output) are rich text boxes.
class ServiceCardBlock(blocks.StructBlock):
    # Optional anchor used for in-page links; falls back to title or a default if blank.
    slug = blocks.CharBlock(
        required=False,
        help_text=(
            "Optional anchor id (e.g. 'event-planning'). "
            "If left blank, the title will be slugified."
        ),
    )

    # Title now optional
    title = blocks.CharBlock(
        required=False,
        max_length=120,
        help_text="Service offering title (optional)",
    )

    # 1) Body – description / background
    details = blocks.RichTextBlock(
        required=True,
        help_text="Service description / background",
    )

    # 2) Offering: body text
    offering = blocks.RichTextBlock(
        required=False,
        help_text="What you actually offer under this service",
    )

    # Optional image, shown under the Offering part
    image = ImageChooserBlock(
        required=False,
        help_text="Image for this service (shown under the Offering section)",
    )

    # 3) Example: body text
    example = blocks.RichTextBlock(
        required=False,
        help_text="Example or case description for this service",
    )

    # 4) Output: body text
    output = blocks.RichTextBlock(
        required=False,
        help_text="Outputs / results you deliver; can include bullet lists",
    )

    class Meta:
        label = "Service card"
        icon = "cog"


class CommunicationPage(Page):
    """
    A single Communication page that can contain an introductory paragraph,
    a list of flexible service cards, an optional row of project highlights,
    and an optional section of embedded videos (Instagram, YouTube, etc.).
    """
    template = "communication.html"

    intro = RichTextField(blank=True, help_text="Optional introductory text.")

    services = StreamField(
        [("service", ServiceCardBlock())],
        blank=True,
        null=True,
        use_json_field=True,
        help_text="Add, remove or reorder services.",
    )

    project_highlights = StreamField(
        [("highlight", ExampleItemBlock())],
        blank=True,
        null=True,
        use_json_field=True,
        help_text="Optional highlights row at the end (e.g. Techfestival, OpenNext).",
    )

    instagram_reels = StreamField(
        [("video", VideoEmbedBlock())],
        blank=True,
        null=True,
        use_json_field=True,
        help_text="Optional embedded videos (Instagram, YouTube, Vimeo, TikTok, etc.) shown at the bottom.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("services"),
        FieldPanel("project_highlights"),
        FieldPanel("instagram_reels"),
    ]
