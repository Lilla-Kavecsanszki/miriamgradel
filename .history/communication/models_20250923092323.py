from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page


# A simple block representing an example or project highlight.
class ExampleItemBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True, max_length=120)
    description = blocks.TextBlock(required=False)
    image = ImageChooserBlock(required=False)
    link_label = blocks.CharBlock(required=False, max_length=80)
    link_url = blocks.URLBlock(required=False)

    class Meta:
        label = "Example / Project"
        icon = "snippet"


# One service offering. Editors can enter a title, description,
# optional hero image, multiple outputs and multiple example items.
class ServiceCardBlock(blocks.StructBlock):
    # Optional anchor used for in‑page links; falls back to the title if blank.
    slug = blocks.CharBlock(
        required=False,
        help_text="Optional anchor id (e.g. 'event-planning'). "
                  "If left blank, the title will be slugified."
    )
    title = blocks.CharBlock(
        required=True,
        max_length=120,
        help_text="Service offering title"
    )
    details = blocks.RichTextBlock(
        required=True,
        help_text="Service description / details"
    )
    image = ImageChooserBlock(
        required=False,
        help_text="Header image for this service"
    )

    # A list of example projects or case studies.
    examples = blocks.ListBlock(
        ExampleItemBlock(),
        required=False,
        help_text="Examples / Projects"
    )

    # A list of outputs or tasks delivered under this service.
    outputs = blocks.ListBlock(
        blocks.CharBlock(label="Output / Task"),
        required=False,
        help_text="Outputs / tasks you deliver"
    )

    class Meta:
        label = "Service card"
        icon = "cog"


class CommunicationPage(Page):
    """
    A single Communication page that can contain an introductory paragraph,
    a list of flexible service cards, and an optional row of project highlights.
    """
    template = "communication.html"

    intro = RichTextField(blank=True, help_text="Optional introductory text.")

    services = StreamField(
        [("service", ServiceCardBlock())],
        blank=True,
        null=True,
        use_json_field=True,
        help_text="Add, remove or reorder services."
    )

    project_highlights = StreamField(
        [("highlight", ExampleItemBlock())],
        blank=True,
        null=True,
        use_json_field=True,
        help_text="Optional highlights row at the end (e.g. Techfestival, OpenNext)"
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("services"),
        FieldPanel("project_highlights"),
    ]
