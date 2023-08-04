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
import django_sql_dashboard
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView

import findthatcharity.apps.addtocsv.views
import findthatcharity.apps.charity.urls
import findthatcharity.apps.ftc.urls
import findthatcharity.apps.ftc.views
import findthatcharity.apps.ftcprofile.urls
import findthatcharity.apps.reconcile.urls
from findthatcharity.api.endpoints import api

handler404 = "findthatcharity.views.missing_page_handler"

urlpatterns = [
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path("accounts/", include(findthatcharity.apps.ftcprofile.urls)),
    path("accounts/", include("django_registration.backends.activation.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/clearcache/", include("clearcache.urls")),
    path("admin/", admin.site.urls, name="admin"),
    path("", findthatcharity.apps.ftc.views.index, name="index"),
    path("about", findthatcharity.apps.ftc.views.about, name="about"),
    path("adddata/", findthatcharity.apps.addtocsv.views.index, name="csvtool"),
    path("api/v1/", api.urls),
    path("orgid/", include(findthatcharity.apps.ftc.urls)),
    path("charity/", include(findthatcharity.apps.charity.urls)),
    path(
        "company/<str:company_number>",
        findthatcharity.apps.ftc.views.company_detail,
        {"filetype": "html"},
        name="company_detail",
    ),
    path("reconcile/", include(findthatcharity.apps.reconcile.urls)),
    path(
        "reconcile",
        findthatcharity.apps.reconcile.views.index,
        {"orgtype": "registered-charity"},
    ),
    path("dashboard/", include(django_sql_dashboard.urls)),
    path("markdownx/", include("markdownx.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
]
