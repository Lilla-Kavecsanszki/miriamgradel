from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.images.models import Image
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.admin.panels import FieldPanel


class HomePage(Page):
    intro = RichTextField(blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        ImageChooserPanel("image"),
    ]
