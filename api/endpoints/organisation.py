from typing import List

from django.shortcuts import Http404, get_object_or_404
from ninja import Router, Query

from api.filters import OrganisationIn
from api.schema import Organisation as OrganisationOut
from api.schema import Source as SourceOut
from api.schema import (
    ResultError,
    OrganisationListResultSuccess,
    # OrganisationResultSuccess,
)
from ftc.models import Organisation
from ftc.query import get_linked_organisations as query_linked_organisations
from ftc.query import get_organisation as query_organisation, OrganisationSearch

organisation_router = Router()


@organisation_router.get(
    "/",
    response={200: OrganisationListResultSuccess, 404: ResultError},
    summary="Search for organisations",
)
def get_organisation_list(
    request,
    filters: OrganisationIn = Query({}),
):
    s = OrganisationSearch(
        results_per_page=filters.limit,
    )
    s.set_criteria(
        term=filters.term,
        source=filters.source,
        active=filters.active,
        domain=filters.domain,
        postcode=filters.postcode,
        location=filters.location,
        other_orgtypes=filters.organisationType,
    )
    s.run_es(with_pagination=True)
    response = s.paginator.page(filters.page)
    results = [hit.__dict__["_d_"] for hit in response.object_list]
    return {
        "success": True,
        "data": results,
    }


@organisation_router.get(
    "/{organisation_id}",
    response={200: OrganisationOut, 404: ResultError},
)
def get_organisation(request, organisation_id: str):
    try:
        return query_organisation(organisation_id)
    except Http404 as e:
        return 404, {"error": str(e), "params": {"organisation_id": organisation_id}}


@organisation_router.get(
    "/{organisation_id}/linked",
    response={200: List[OrganisationOut], 404: ResultError},
)
def get_linked_organisations(request, organisation_id: str):
    try:
        orgs = query_linked_organisations(organisation_id)
        return orgs.records
    except Http404 as e:
        return 404, {"error": str(e), "params": {"organisation_id": organisation_id}}


@organisation_router.get(
    "/{organisation_id}/source",
    response={200: SourceOut, 404: ResultError},
)
def get_organisation_source(request, organisation_id: str):
    try:
        organisation = get_object_or_404(Organisation, org_id=organisation_id)
        return organisation.source
    except Http404 as e:
        return 404, {"error": str(e), "params": {"organisation_id": organisation_id}}
