from django.urls import path

from . import views

urlpatterns = [
    path("_reconcile", views.company_reconcile),
    path(
        "<str:company_number>",
        views.company_detail,
        {"filetype": "html"},
        name="company_detail",
    ),
]
