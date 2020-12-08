from typing import List
import django_filters as filters
from ninja import Schema
from ftc.models import Organisation


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class OrganisationFilter(filters.FilterSet):
    organisationType = CharInFilter(lookup_expr='overlap')

    class Meta:
        model = Organisation
        fields = ['active', 'geo_laua', 'organisationType']


class OrganisationIn(Schema):
    organisationType: List[str] = None
    geo_laua: str = None
    active: bool = True
    page: int = 1
    limit: int = 10
