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

from findthatcharity.apps.ftcprofile import views

urlpatterns = [
    path(
        "profile/",
        views.account_profile,
        name="account_profile",
    ),
    path(
        "profile/apikey",
        views.api_key_edit,
        name="api_key_edit",
    ),
    path(
        "profile/tag_organisation/<str:org_id>",
        views.tag_organisation,
        name="tag_organisation",
    ),
]