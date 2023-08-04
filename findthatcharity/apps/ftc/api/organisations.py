from typing import List

from django.core.paginator import Paginator
from django.shortcuts import Http404, get_object_or_404
from ninja import Query, Schema
from ninja_extra import api_controller, http_get, http_post

from findthatcharity.api.base import APIControllerBase, default_response
from findthatcharity.apps.ftc.api.filters import OrganisationFilter, OrganisationIn
from findthatcharity.apps.ftc.api.filters import (
    OrganisationSearch as OrganisationSearchIn,
)
from findthatcharity.apps.ftc.api.schema import Organisation as OrganisationOut
from findthatcharity.apps.ftc.api.schema import (
    OrganisationGroup as OrganisationGroupOut,
)
from findthatcharity.apps.ftc.api.schema import Source as SourceOut
from findthatcharity.apps.ftc.documents import OrganisationGroup
from findthatcharity.apps.ftc.models import Organisation
from findthatcharity.apps.ftc.query import OrganisationSearch
from findthatcharity.apps.ftc.query import (
    get_linked_organisations as query_linked_organisations,
)
from findthatcharity.apps.ftc.query import get_organisation as query_organisation
from findthatcharity.apps.ftc.query import random_query as query_random_organisation
from findthatcharity.utils import url_replace


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


class OrganisationSearchResult(OrganisationResultList):
    result: List[OrganisationGroupOut]


class SourceResult(Schema):
    success: bool = True
    error: str = None
    params: dict = {}
    result: SourceOut


MAX_LIMIT = 50


@api_controller(
    "/organisations",
    tags=["Organisations"],
)
class API(APIControllerBase):
    def _get_organisation_list(self, request, filters: OrganisationIn = Query({})):
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
        "",
        summary="Get list of organisations",
        response={200: OrganisationResultList, **default_response},
    )
    def get_organisation_list(self, request, filters: OrganisationIn = Query({})):
        return self._get_organisation_list(request, filters)

    @http_post(
        "",
        summary="Get list of organisations",
        description="This uses POST to allow for larger query strings",
        response={200: OrganisationResultList, **default_response},
    )
    def get_organisation_list_post_version(
        self, request, filters: OrganisationIn = Query({})
    ):
        return self._get_organisation_list(request, filters)

    @http_get(
        "/_search",
        response={200: OrganisationSearchResult, **default_response},
    )
    def organisation_search(self, request, filters: OrganisationSearchIn = Query({})):
        if filters.limit > MAX_LIMIT:
            filters.limit = MAX_LIMIT
        s = OrganisationSearch(results_per_page=filters.limit)
        filters.set_criteria(s)
        s.run_es(with_pagination=True, with_aggregation=True)
        response = s.paginator.get_page(filters.page)
        result_list = [
            {**r.to_dict(), "score": r.meta.score} for r in response.object_list
        ]
        return {
            "error": None,
            "params": filters.dict(),
            "count": s.paginator.count,
            "result": result_list,
            "next": url_replace(request, page=response.next_page_number())
            if response.has_next()
            else None,
            "previous": url_replace(request, page=response.previous_page_number())
            if response.has_previous()
            else None,
        }

    @http_get(
        "/_random",
        response={200: OrganisationResult, **default_response},
    )
    def get_random_organisation(
        self,
        request,
        active_only: bool = Query(False),
        organisation_type: str = Query("registered-charity"),
    ):
        """Get a random charity record"""
        q = OrganisationGroup.search().from_dict(
            query_random_organisation(active_only, organisation_type)
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
        response={200: OrganisationResult, **default_response},
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
        response={200: OrganisationResult, **default_response},
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
        response={200: OrganisationResultList, **default_response},
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
        response={200: SourceResult, **default_response},
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
