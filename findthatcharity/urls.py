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

import addtocsv.views
import charity.urls
import ftc.urls
import ftc.views
import reconcile.urls
from findthatcharity.endpoints import api

handler404 = "findthatcharity.views.missing_page_handler"

urlpatterns = [
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path("accounts/", include("ftcprofile.urls")),
    path("accounts/", include("django_registration.backends.activation.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls, name="admin"),
    path("", ftc.views.index, name="index"),
    path("about", ftc.views.about, name="about"),
    path("adddata/", addtocsv.views.index, name="csvtool"),
    path("adddata/company/", addtocsv.views.companies, name="csvtool_company"),
    path("api/v1/", api.urls),
    path("orgid/", include(ftc.urls)),
    path("charity/", include(charity.urls)),
    path(
        "company/<str:company_number>",
        ftc.views.company_detail,
        {"filetype": "html"},
        name="company_detail",
    ),
    path("reconcile/", include(reconcile.urls)),
    path("reconcile", reconcile.views.index, {"orgtype": "registered-charity"}),
    path("dashboard/", include(django_sql_dashboard.urls)),
    path("markdownx/", include("markdownx.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
]
