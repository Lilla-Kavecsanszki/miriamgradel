from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


# -------- Shared blocks --------

class ExampleItemBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True, max_length=120)
    description = blocks.TextBlock(required=False)
    image = ImageChooserBlock(required=False)
    link_label = blocks.CharBlock(required=False, max_length=80)
    link_url = blocks.URLBlock(required=False)

    class Meta:
        label = "Example / Project"
        icon = "snippet"


class ServiceCardBlock(blocks.StructBlock):
    slug = blocks.CharBlock(required=False, help_text="Optional anchor id (e.g. 'event-moderation')")
    title = blocks.CharBlock(required=True, max_length=120, help_text="Service offering title")
    details = blocks.RichTextBlock(required=True, help_text="Service description / details")
    image = ImageChooserBlock(required=False, help_text="Header image for this service")

    examples = blocks.ListBlock(ExampleItemBlock(), required=False, help_text="Examples / Projects")
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
    Single Communication page with service cards + optional project highlights
    """
    template = "communication.html"

    intro = RichTextField(blank=True)

    services = StreamField(
        [("service", ServiceCardBlock())],
        use_json_field=True,
        blank=True,
        null=True,
    )

    # Optional highlights row at the end (e.g. Techfestival, OpenNext, Dansehallerne)
    project_highlights = StreamField(
        [("highlight", ExampleItemBlock())],
        use_json_field=True,
        blank=True,
        null=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("services"),
        FieldPanel("project_highlights"),
    ]
