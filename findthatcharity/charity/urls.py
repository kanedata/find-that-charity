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

from . import views

urlpatterns = [
    path('<str:regno>.json', views.get_charity, {"filetype": "json"}),
    path('<str:regno>.html', views.get_charity, {"filetype": "html"}),
    path('<str:regno>', views.get_charity, {
         "filetype": "html"}, name='charity_html'),
    path('<str:regno>/preview', views.get_charity, {
         "filetype": "html", "preview": True}, name='charity_html_preview'),
]
