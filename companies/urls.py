from django.urls import path

from . import views

urlpatterns = [
    path("<str:company_number>", views.company_detail, {"filetype": "html"}),
]
