from typing import List

import django_filters as filters
from ninja import Schema

from ftc.models import Organisation


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class OrganisationFilter(filters.FilterSet):
    organisationType = CharInFilter(lookup_expr="overlap")
    org_id = filters.CharFilter(method="filter_in_list")

    def filter_in_list(self, qs, name, value):
        return qs.filter(**{f"{name}__in": self.request.GET.getlist(name)})

    class Meta:
        model = Organisation
        fields = ["active", "organisationType"]


class OrganisationIn(Schema):
    organisationType: List[str] = None
    org_id: List[str] = None
    active: bool = True
    page: int = 1
    limit: int = 10
