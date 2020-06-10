from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, {
         'orgtype': 'registered-charity'}, name='reconcile'),
    path('/propose_properties', views.propose_properties),
    path('/suggest', views.suggest, {
         'orgtype': 'registered-charity'}),
    path('/<str:orgtype>/suggest', views.suggest),
    path('/<str:orgtype>', views.index),
]
