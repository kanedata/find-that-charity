from rest_framework import viewsets
import django_filters as filters

from api.serializers import OrganisationSerializer, OrganisationTypeSerializer
from ftc.models import Organisation, OrganisationType


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class OrganisationFilter(filters.FilterSet):
    organisationType = CharInFilter(lookup_expr='overlap')

    class Meta:
        model = Organisation
        fields = ['active', 'geo_laua', 'organisationType']


class OrganisationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows organisations to be viewed.
    """
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    lookup_field = 'org_id'
    filter_backends = [filters.rest_framework.DjangoFilterBackend]
    filterset_class = OrganisationFilter


class OrganisationTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows organisations to be viewed.
    """
    queryset = OrganisationType.objects.all()
    serializer_class = OrganisationTypeSerializer
    lookup_field = 'slug'
