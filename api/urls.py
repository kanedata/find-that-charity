from django.urls import include, path
from rest_framework import routers
from api import views


router = routers.DefaultRouter()
router.register(r'organisations', views.OrganisationViewSet)
router.register(r'organisation-types', views.OrganisationTypeViewSet, basename='organisation-types')

urlpatterns = [
    path('', include(router.urls)),
]
