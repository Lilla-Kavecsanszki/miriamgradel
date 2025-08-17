from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from modelcluster.fields import ParentalManyToManyField

# Your BTS model
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

    # Adjust to where you want to place the index
    parent_page_types = ["home.HomePage"]
    subpage_types = ["journalism.WrittenArticlePage"]

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        # All live children, newest first
        articles = (
            self.get_children()
            .live()
            .specific()
            .order_by("-first_published_at", "-latest_revision_created_at")
        )
        ctx["articles"] = articles

        # Latest BTS items for the sidebar
        ctx["bts_items"] = (
            Page.objects.live()
            .type(BTSPage)          # ✅ use the class you actually imported
            .specific()
            .order_by("-first_published_at")[:3]
        )
        return ctx


class WrittenArticlePage(Page):
    """
    A single article. If 'external_url' is set, the index links out to it.
    Otherwise it links to this page's detail.
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

    # Optional: connect BTS pages related to this article
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


# Audio episodes
class AudioItem(blocks.StructBlock):
    title = blocks.CharBlock(required=True, max_length=200)
    date = blocks.DateBlock(required=False)
    embed = EmbedBlock(required=True, help_text="Paste the episode embed URL (Spotify, SoundCloud, etc.)")
    image = ImageChooserBlock(required=False)
    teaser = blocks.TextBlock(required=False)
    behind_scenes = BehindScenesLink(required=False)

    class Meta:
        icon = "media"
        label = "Audio episode"


# Videos
class VideoItem(blocks.StructBlock):
    title = blocks.CharBlock(required=True, max_length=200)
    date = blocks.DateBlock(required=False)
    embed = EmbedBlock(required=True, help_text="Paste the video URL (YouTube, Vimeo, Instagram reel link, etc.)")
    image = ImageChooserBlock(required=False, help_text="Optional cover image (used if embed has no thumbnail)")
    orientation = blocks.ChoiceBlock(required=False, choices=[("auto","Auto"),("landscape","Landscape"),("portrait","Portrait")], default="auto")
    teaser = blocks.TextBlock(required=False)
    behind_scenes = BehindScenesLink(required=False)

    class Meta:
        icon = "media"
        label = "Video"


# ---- Pages (no parent “Journalism” page needed) ----

class WrittenPage(Page):
    template = "written_page.html"

    intro = RichTextField(blank=True)
    articles = StreamField([("article", ArticleItem())], use_json_field=True, blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("articles"),
    ]


class AudioPage(Page):
    template = "audio_page.html"

    intro = RichTextField(blank=True)
    episodes = StreamField([("episode", AudioItem())], use_json_field=True, blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("episodes"),
    ]


class VideoPage(Page):
    template = "video_page.html"

    intro = RichTextField(blank=True)
    videos = StreamField([("video", VideoItem())], use_json_field=True, blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("videos"),
    ]
