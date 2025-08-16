from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from django.db import models


class WorkWithMePage(Page):
    template = "work_with_me_page.html"

    greeting = models.CharField(max_length=200, blank=True)
    intro = RichTextField(blank=True)
    portrait = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )
    contact_email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=50, blank=True)

    content_panels = Page.content_panels + [   # <-- keep the title panel!
        FieldPanel("greeting"),
        FieldPanel("intro"),
        FieldPanel("portrait"),
        FieldPanel("contact_email"),
        FieldPanel("phone_number"),
    ]
