from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel


class WelcomePage(Page):
    """
    Landing / splash page.
    Shows full-screen background image + hero text,
    no menu, fade-out to /home.
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

    content_panels = Page.content_panels + [
        FieldPanel("hero_text"),
        FieldPanel("background_image"),
    ]


class HomePage(Page):
    """
    Main homepage with sections stacked vertically.
    Sticky side menu is visible here.
    """
    template = "home_page.html"

    # Add new fields for homepage sections as you need them
    intro_text = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro_text"),
        # Later you can add StreamFields for flexible content blocks
    ]
