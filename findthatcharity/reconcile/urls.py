from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, {
         'orgtype': 'registered-charity'}, name='reconcile'),
    path('/propose_properties', views.propose_properties),
    path('/<str:orgtype>', views.index),
]
