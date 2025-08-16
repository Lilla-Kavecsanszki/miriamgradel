from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.blocks import PageChooserBlock


# ---- Shared blocks ----

class BehindScenesLink(blocks.StructBlock):
    page = PageChooserBlock(required=False, help_text="Optional link to a Behind the Scenes section/page")
    label = blocks.CharBlock(required=False, default="Behind the scenes")

    class Meta:
        icon = "doc-empty-inverse"
        label = "Behind the scenes link"


# Articles
class ArticleItem(blocks.StructBlock):
    title = blocks.CharBlock(required=True, max_length=200)
    publication = blocks.CharBlock(required=False, max_length=120, help_text="Outlet / publication name")
    date = blocks.DateBlock(required=False)
    url = blocks.URLBlock(required=True, help_text="Public link to the article")
    teaser = blocks.TextBlock(required=False)
    image = ImageChooserBlock(required=False)
    behind_scenes = BehindScenesLink(required=False)

    class Meta:
        icon = "doc-full"
        label = "Article"


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
