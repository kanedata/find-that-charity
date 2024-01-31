import json
from typing import Dict

from django.http import HttpResponse
from ninja import Form, Query, Router

from reconcile.api.base import Reconcile

from .schema import (
    DataExtensionPropertyProposalQuery,
    DataExtensionPropertyProposalResponse,
    DataExtensionQuery,
    DataExtensionQueryResponse,
    ReconciliationQueryBatch,
    ReconciliationQueryBatchForm,
    ReconciliationResult,
    ServiceSpec,
    SuggestEntityQuery,
    SuggestResponse,
    SuggestTypeQuery,
)

api = Router(tags=["Reconciliation (nonprofits)"])
reconcile = Reconcile()


@api.get(
    path="",
    response={
        200: ServiceSpec | Dict[str, ReconciliationResult] | DataExtensionQueryResponse
    },
    exclude_none=True,
    summary="Service specification for reconciling against any nonprofit organisation",
    description="Get the service specification for reconciling against any nonprofit organisation",
)
def get_service_spec(request, queries: Query[ReconciliationQueryBatchForm]):
    if queries.queries:
        queries_parsed = ReconciliationQueryBatch(queries=json.loads(queries.queries))
        return reconcile.reconcile(request, queries_parsed, orgtypes="all")
    elif queries.extend:
        queries_parsed = DataExtensionQuery(**json.loads(queries.extend))
        return reconcile.data_extension(request, queries_parsed)
    return reconcile.get_service_spec(request, orgtypes="all")


@api.post(
    "",
    response={200: Dict[str, ReconciliationResult] | DataExtensionQueryResponse},
    exclude_none=True,
    summary="Reconciliation endpoint for reconciling against any nonprofit organisation",
    description="Reconciling queries against any nonprofit organisation.",
)
def reconcile_entities(request, queries: Form[ReconciliationQueryBatchForm]):
    if queries.queries:
        queries_parsed = ReconciliationQueryBatch(queries=json.loads(queries.queries))
        return reconcile.reconcile(request, queries_parsed, orgtypes="all")
    elif queries.extend:
        queries_parsed = DataExtensionQuery(**json.loads(queries.extend))
        return reconcile.data_extension(request, queries_parsed)


@api.get("/preview")
def preview(request, id: str, response: HttpResponse):
    return reconcile.preview_view(request, id, response)


@api.get("/suggest/entity", response={200: SuggestResponse}, exclude_none=True)
def suggest_entity(request, query: Query[SuggestEntityQuery]):
    return reconcile.suggest_entity(
        request, query.prefix, query.cursor, orgtypes=query.type
    )


@api.get("/suggest/type", response={200: SuggestResponse}, exclude_none=True)
def suggest_type(request, query: Query[SuggestTypeQuery]):
    return reconcile.suggest_type(request, query.prefix, query.cursor)


@api.get(
    "/extend/propose",
    response={200: DataExtensionPropertyProposalResponse},
    exclude_none=True,
)
def propose_properties(request, query: Query[DataExtensionPropertyProposalQuery]):
    return reconcile.propose_properties(request, type_=query.type, limit=query.limit)


# @api.post(
#     "/extend",
#     response={200: DataExtensionQueryResponse},
#     exclude_none=True,
# )
# def data_extension(request, body: DataExtensionQuery):
#     return reconcile.data_extension(request, body)
