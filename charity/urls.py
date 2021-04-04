from django.urls import path

from . import views

urlpatterns = [
    path("<str:regno>.json", views.get_charity, {"filetype": "json"}),
    path("<str:regno>.html", views.get_charity, {"filetype": "html"}),
    path("<str:regno>", views.get_charity, {"filetype": "html"}, name="charity_html"),
    path(
        "<str:regno>/preview",
        views.get_charity,
        {"filetype": "html", "preview": True},
        name="charity_html_preview",
    ),
]
