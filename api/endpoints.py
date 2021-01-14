from typing import List

from django.core.paginator import Paginator
from django.shortcuts import Http404, get_object_or_404
from ninja import NinjaAPI, Query, Schema

from api.filters import OrganisationFilter, OrganisationIn
from api.schema import Organisation as OrganisationOut
from api.schema import Source as SourceOut
from ftc.models import Organisation
from ftc.query import get_linked_organisations as query_linked_organisations
from ftc.query import get_organisation as query_organisation

api = NinjaAPI(
    title="Find that Charity API",
    description="Search for information about charities and other non-profit organisations",
    version="1.0",
)


class ResultError(Schema):
    error: str
    params: dict


@api.get("/organisations", response={200: List[OrganisationOut], 404: ResultError})
def get_organisation_list(request, filters: OrganisationIn = Query({})):
    filters = filters.dict()
    f = OrganisationFilter(request.GET, queryset=Organisation.objects.all())
    paginator = Paginator(f.qs, filters["limit"])
    response = paginator.page(filters["page"])
    return response.object_list


@api.get(
    "/organisations/{organisation_id}",
    response={200: OrganisationOut, 404: ResultError},
)
def get_organisation(request, organisation_id: str):
    try:
        return query_organisation(organisation_id)
    except Http404 as e:
        return 404, {"error": str(e), "params": {"organisation_id": organisation_id}}


@api.get(
    "/organisations/{organisation_id}/linked",
    response={200: List[OrganisationOut], 404: ResultError},
)
def get_linked_organisations(request, organisation_id: str):
    try:
        orgs = query_linked_organisations(organisation_id)
        return orgs.records
    except Http404 as e:
        return 404, {"error": str(e), "params": {"organisation_id": organisation_id}}


@api.get(
    "/organisations/{organisation_id}/source",
    response={200: SourceOut, 404: ResultError},
)
def get_organisation_source(request, organisation_id: str):
    try:
        organisation = get_object_or_404(Organisation, org_id=organisation_id)
        return organisation.source
    except Http404 as e:
        return 404, {"error": str(e), "params": {"organisation_id": organisation_id}}
