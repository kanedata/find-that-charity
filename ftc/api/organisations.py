from typing import List

from django.core.paginator import Paginator
from django.shortcuts import Http404, get_object_or_404
from ninja import Query, Schema
from ninja_extra import api_controller, http_generic, http_get

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


@api_controller(
    "/organisations",
    tags=["Organisations"],
)
class API:
    @http_generic(
        "",
        methods=["GET", "POST"],
        response={200: OrganisationResultList, 404: ResultError},
    )
    def get_organisation_list(self, request, filters: OrganisationIn = Query({})):
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

    @http_get(
        "/_random",
        response={200: OrganisationResult, 404: ResultError},
    )
    def get_random_organisation(self, request, active_only: bool = Query(False)):
        """Get a random charity record"""
        q = OrganisationGroup.search().from_dict(
            query_random_organisation(active_only, "registered-charity")
        )[0]
        result = q.execute()
        for r in result:
            return {
                "error": None,
                "params": {
                    "active_only": active_only,
                },
                "result": query_organisation(r.org_id),
            }

    @http_get(
        "/{organisation_id}",
        response={200: OrganisationResult, 404: ResultError},
    )
    def get_organisation(self, request, organisation_id: str):
        try:
            return {
                "error": None,
                "params": {
                    "org_id": organisation_id,
                },
                "result": query_organisation(organisation_id),
            }
        except Http404 as e:
            return 404, {
                "error": str(e),
                "params": {"organisation_id": organisation_id},
            }

    @http_get(
        "/{organisation_id}/canonical",
        response={200: OrganisationResult, 404: ResultError},
    )
    def get_canonical_organisation(self, request, organisation_id: str):
        orgs = query_linked_organisations(organisation_id)
        try:
            return {
                "error": None,
                "params": {
                    "org_id": organisation_id,
                },
                "result": orgs.records[0],
            }
        except Http404 as e:
            return 404, {
                "error": str(e),
                "params": {"organisation_id": organisation_id},
            }

    @http_get(
        "/{organisation_id}/linked",
        response={200: OrganisationResultList, 404: ResultError},
    )
    def get_linked_organisations(self, request, organisation_id: str):
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
            return 404, {
                "error": str(e),
                "params": {"organisation_id": organisation_id},
            }

    @http_get(
        "/{organisation_id}/source",
        response={200: SourceResult, 404: ResultError},
    )
    def get_organisation_source(self, request, organisation_id: str):
        try:
            organisation = get_object_or_404(Organisation, org_id=organisation_id)
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
