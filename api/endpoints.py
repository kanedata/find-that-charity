from typing import List

from django.core.paginator import Paginator
from django.shortcuts import Http404, get_object_or_404
from ninja import NinjaAPI, Query, Schema

from api.filters import OrganisationFilter, OrganisationIn
from api.schema import Organisation as OrganisationOut
from api.schema import Source as SourceOut
from findthatcharity.utils import url_replace
from ftc.models import Organisation
from ftc.query import get_linked_organisations as query_linked_organisations
from ftc.query import get_organisation as query_organisation

api = NinjaAPI(
    title="Find that Charity API",
    description="Search for information about charities and other non-profit organisations",
    version="1.0",
)


class ResultError(Schema):
    success: bool = False
    error: str = None
    params: dict = {}
    result: List = None


class OrganisationResult(Schema):
    success: bool = True
    error: str = None
    params: dict = {}
    result: OrganisationOut


class OrganisationResultList(Schema):
    success: bool = True
    error: str = None
    params: dict = {}
    count: int = 0
    next: str = None
    previous: str = None
    result: List[OrganisationOut]


class SourceResult(Schema):
    success: bool = True
    error: str = None
    params: dict = {}
    result: SourceOut


@api.api_operation(
    ["GET", "POST"],
    "/organisations",
    response={200: OrganisationResultList, 404: ResultError},
    tags=["Organisations"],
)
def get_organisation_list(request, filters: OrganisationIn = Query({})):
    filters = filters.dict()
    f = OrganisationFilter(
        request.GET,
        queryset=Organisation.objects.prefetch_related("organisationTypePrimary"),
        request=request,
    )
    paginator = Paginator(f.qs, filters["limit"])
    response = paginator.page(filters["page"])
    return {
        "error": None,
        "params": filters,
        "count": paginator.count,
        "result": list(response.object_list),
        "next": url_replace(request, page=response.next_page_number())
        if response.has_next()
        else None,
        "previous": url_replace(request, page=response.previous_page_number())
        if response.has_previous()
        else None,
    }


@api.get(
    "/organisations/{organisation_id}",
    response={200: OrganisationResult, 404: ResultError},
    tags=["Organisations"],
)
def get_organisation(request, organisation_id: str):
    try:
        return {
            "error": None,
            "params": {
                "org_id": organisation_id,
            },
            "result": query_organisation(organisation_id),
        }
    except Http404 as e:
        return 404, {"error": str(e), "params": {"organisation_id": organisation_id}}


@api.get(
    "/organisations/{organisation_id}/linked",
    response={200: OrganisationResultList, 404: ResultError},
    tags=["Organisations"],
)
def get_linked_organisations(request, organisation_id: str):
    try:
        orgs = query_linked_organisations(organisation_id)
        return {
            "error": None,
            "params": {
                "org_id": organisation_id,
            },
            "count": len(orgs.records),
            "result": orgs.records,
            "next": None,
            "previous": None,
        }
    except Http404 as e:
        return 404, {"error": str(e), "params": {"organisation_id": organisation_id}}


@api.get(
    "/organisations/{organisation_id}/source",
    response={200: SourceOut, 404: ResultError},
    tags=["Organisations"],
)
def get_organisation_source(request, organisation_id: str):
    try:
        organisation = get_object_or_404(Organisation, org_id=organisation_id)
        return organisation.source
    except Http404 as e:
        return 404, {"error": str(e), "params": {"organisation_id": organisation_id}}
