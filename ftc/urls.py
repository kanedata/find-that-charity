"""findthatcharity URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from . import feeds, views

urlpatterns = [
    path("random", views.get_random_org, name="random_org"),
    path(
        "all.csv",
        views.orgid_type,
        {"filetype": "csv"},
        name="orgid_all_download",
    ),
    path(
        "type/<slug:orgtype>.csv",
        views.orgid_type,
        {"filetype": "csv"},
        name="orgid_type_download",
    ),
    path("type/<slug:orgtype>.html", views.orgid_type),
    path("type/<slug:orgtype>", views.orgid_type, name="orgid_type"),
    path(
        "source/<str:source>.csv",
        views.orgid_type,
        {"filetype": "csv"},
        name="orgid_source_download",
    ),
    path("source/<str:source>.html", views.orgid_type),
    path("source/<str:source>", views.orgid_type, name="orgid_source"),
    path("scrapes/feed.rss", feeds.ScrapesFeedRSS()),
    path("scrapes/feed.atom", feeds.ScrapesFeedAtom()),
    path("<path:org_id>/canonical.json", views.get_orgid_canon),
    path("<path:org_id>.json", views.get_org_by_id, {"filetype": "json"}),
    path("<path:org_id>.html", views.get_org_by_id, {"filetype": "html"}),
    path(
        "<path:org_id>/preview",
        views.get_org_by_id,
        {"filetype": "html", "preview": True},
        name="orgid_html_preview",
    ),
    path("<path:org_id>", views.get_org_by_id, {"filetype": "html"}, name="orgid_html"),
]
