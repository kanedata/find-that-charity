from typing import List, Optional

from django.core.paginator import Paginator
from django.shortcuts import Http404, get_object_or_404
from ninja import Query, Router, Schema

from findthatcharity.utils import url_replace
from ftc.api.filters import OrganisationFilter, OrganisationIn
from ftc.api.schema import Organisation as OrganisationOut
from ftc.api.schema import Source as SourceOut
from ftc.documents import OrganisationGroup
from ftc.models import Organisation
from ftc.query import get_linked_organisations as query_linked_organisations
from ftc.query import get_organisation as query_organisation
from ftc.query import random_query as query_random_organisation


class ResultError(Schema):
    success: bool = False
    error: Optional[str] = None
    params: dict = {}
    result: Optional[List] = None


class OrganisationResult(Schema):
    success: bool = True
    error: Optional[str] = None
    params: dict = {}
    result: OrganisationOut


class OrganisationResultList(Schema):
    success: bool = True
    error: Optional[str] = None
    params: dict = {}
    count: int = 0
    next: Optional[str] = None
    previous: Optional[str] = None
    result: List[OrganisationOut]

    @staticmethod
    def resolve_result(obj):
        results = []
        for r in obj.get("result", {}).get("results", []):
            r._request = obj.get("result", {}).get("request")
            results.append(r)
        return results


class SourceResult(Schema):
    success: bool = True
    error: Optional[str] = None
    params: dict = {}
    result: SourceOut


api = Router(tags=["Organisations"])


@api.api_operation(
    methods=["GET", "POST"],
    path="",
    response={200: OrganisationResultList, 404: ResultError},
)
def get_organisation_list(request, filters: OrganisationIn = Query({})):
    filters = filters.dict()
    f = OrganisationFilter(
        request.GET,
        queryset=Organisation.objects.prefetch_related("organisationTypePrimary"),
        request=request,
    )
    paginator = Paginator(f.qs.order_by("name"), filters["limit"])
    response = paginator.page(filters["page"])
    return {
        "error": None,
        "params": filters,
        "count": paginator.count,
        "result": {"results": list(response.object_list), "request": request},
        "next": (
            url_replace(request, page=response.next_page_number())
            if response.has_next()
            else None
        ),
        "previous": (
            url_replace(request, page=response.previous_page_number())
            if response.has_previous()
            else None
        ),
    }


@api.get(
    "/_random",
    response={200: OrganisationResult, 404: ResultError},
)
def get_random_organisation(
    request,
    active_only: bool = Query(False),
    organisation_type: str = Query("registered-charity"),
):
    """Get a random charity record"""
    q = OrganisationGroup.search().update_from_dict(
        query_random_organisation(active_only, organisation_type)
    )[0]
    result = q.execute()
    for r in result:
        organisation = query_organisation(r.org_id)
        organisation._request = request
        return {
            "error": None,
            "params": {
                "active_only": active_only,
            },
            "result": organisation,
        }


@api.get(
    "/{path:organisation_id}",
    response={200: OrganisationResult, 404: ResultError},
)
def get_organisation(request, organisation_id: str):
    try:
        organisation = query_organisation(organisation_id)
        organisation._request = request
        return {
            "error": None,
            "params": {
                "org_id": organisation_id,
            },
            "result": organisation,
        }
    except Http404 as e:
        return 404, {
            "error": str(e),
            "params": {"organisation_id": organisation_id},
        }


@api.get(
    "/{path:organisation_id}/canonical",
    response={200: OrganisationResult, 404: ResultError},
)
def get_canonical_organisation(request, organisation_id: str):
    orgs = query_linked_organisations(organisation_id)
    try:
        organisation = orgs.records[0]
        organisation._request = request
        return {
            "error": None,
            "params": {
                "org_id": organisation_id,
            },
            "result": organisation,
        }
    except Http404 as e:
        return 404, {
            "error": str(e),
            "params": {"organisation_id": organisation_id},
        }


@api.get(
    "/{path:organisation_id}/linked",
    response={200: OrganisationResultList, 404: ResultError},
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
            "result": {"results": orgs.records, "request": request},
            "next": None,
            "previous": None,
        }
    except Http404 as e:
        return 404, {
            "error": str(e),
            "params": {"organisation_id": organisation_id},
        }


@api.get(
    "/{path:organisation_id}/source",
    response={200: SourceResult, 404: ResultError},
)
def get_organisation_source(request, organisation_id: str):
    try:
        organisation = get_object_or_404(Organisation, org_id=organisation_id)
        organisation._request = request
        return {
            "error": None,
            "params": {
                "org_id": organisation_id,
            },
            "result": organisation.source,
        }
    except Http404 as e:
        return 404, {
            "error": str(e),
            "params": {"organisation_id": organisation_id},
        }
