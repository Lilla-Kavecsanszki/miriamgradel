from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from modelcluster.fields import ParentalManyToManyField

# BTS model
from behind_scenes.models import BTSPage


class WrittenIndexPage(Page):
    """
    Lists WrittenArticlePage children and shows a BTS sidebar.
    """
    template = "journalism/written_index_page.html"

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    # Place this index under Home (adjust if needed)
    parent_page_types = ["home.HomePage"]
    subpage_types = ["journalism.WrittenArticlePage"]

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        # children = the articles
        ctx["articles"] = (
            self.get_children()
            .live()
            .specific()
            .order_by("-first_published_at", "-latest_revision_created_at")
        )
        # latest BTS items for sidebar
        ctx["bts_items"] = (
            BTSPage.objects.live()
            .specific()
            .order_by("-first_published_at")[:3]
        )
        return ctx


class WrittenArticlePage(Page):
    """
    A single article. If 'external_url' is set, the index links to it;
    otherwise it links to this page detail.
    """
    template = "journalism/written_article_page.html"

    publication_name = models.CharField(
        max_length=150, blank=True, help_text="e.g. The Sun"
    )
    publication_date = models.DateField(null=True, blank=True)
    external_url = models.URLField(
        blank=True, help_text="If set, the index links out to this URL."
    )
    excerpt = models.TextField(blank=True)

    # optionally attach BTS pages related to this article
    related_bts = ParentalManyToManyField(
        "behind_scenes.BTSPage", blank=True, related_name="related_articles"
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("publication_name"),
                FieldPanel("publication_date"),
                FieldPanel("external_url"),
                FieldPanel("excerpt"),
                FieldPanel("related_bts"),
            ],
            heading="Article info",
        ),
    ]

    parent_page_types = ["journalism.WrittenIndexPage"]
    subpage_types = []
