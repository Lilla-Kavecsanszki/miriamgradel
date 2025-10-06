# work_with_me/urls.py
from django.urls import path
from . import views

app_name = "work_with_me"

urlpatterns = [
    path("wme/vcard/<int:page_id>/", views.vcard_inline, name="vcard_inline"),
]
