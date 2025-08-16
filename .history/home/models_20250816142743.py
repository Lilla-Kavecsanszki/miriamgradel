from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class WelcomePage(Page):
    """
    Landing / splash page.
    Shows full-screen background image + hero text,
    no menu, fade-out to chosen destination page.
    """
    template = "welcome_page.html"

    hero_text = RichTextField(blank=True)

    background_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )

    # lets you pick where the Enter button goes (e.g., your HomePage)
    destination_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )

    content_panels = Page.content_panels + [
        FieldPanel("hero_text"),
        FieldPanel("background_image"),
        FieldPanel("destination_page"),
    ]


class ServiceBlock(blocks.StructBlock):
    """
    A single service card with image, title, and description.
    """
    image = ImageChooserBlock(required=True, help_text="Header image for this service")
    title = blocks.CharBlock(required=True, max_length=100, help_text="Service name")
    description = blocks.TextBlock(required=True, help_text="Short description")

    class Meta:
        icon = "cog"
        label = "Service"


class HomePage(Page):
    """
    Main homepage with sections stacked vertically.
    Sticky side menu is visible here.
    """
    template = "home_page.html"

    intro_text = RichTextField(blank=True)
    mission_statement = RichTextField(blank=True)

    services = StreamField(
        [("service", ServiceBlock())],
        null=True,
        blank=True,
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro_text"),
        FieldPanel("mission_statement"),
        FieldPanel("services"),
    ]
