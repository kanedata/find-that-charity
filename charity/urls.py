from django.urls import path

from . import views

urlpatterns = [
    path(
        "export/area/<str:geoarea>/<str:geocode>.xlsx",
        views.export_data,
        {"filetype": "xlsx"},
    ),
    path(
        "export/area/<str:geoarea>/<str:geocode>.sqlite",
        views.export_data,
        {"filetype": "sqlite"},
    ),
    path(
        "export/area/<str:geoarea>/<str:geocode>.db",
        views.export_data,
        {"filetype": "sqlite"},
    ),
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
