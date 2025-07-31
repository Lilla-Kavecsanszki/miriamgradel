from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.images.models import Image
from wagtail.admin.panels import FieldPanel


class HomePage(Page):
    hero_text = RichTextField(blank=True)

    background_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel("hero_text"),
        FieldPanel("background_image"),
    ]
