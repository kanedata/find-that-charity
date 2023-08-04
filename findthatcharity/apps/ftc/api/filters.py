from typing import List

import django_filters as filters
from ninja import Schema

from findthatcharity.apps.ftc.models import Organisation


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


class OrganisationSearch(Schema):
    organisationType: List[str] = None
    source: List[str] = None
    location: List[str] = None
    q: str = None
    postcode: str = None
    domain: str = None
    active: bool = True
    page: int = 1
    limit: int = 10

    def set_criteria(self, search):
        search.set_criteria(
            term=self.q,
            other_orgtypes=self.organisationType,
            source=self.source,
            active=self.active,
            domain=self.domain,
            postcode=self.postcode,
            location=self.location,
        )
