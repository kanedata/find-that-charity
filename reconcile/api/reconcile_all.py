import json
from typing import Dict

from django.http import HttpResponse
from ninja import Form, Router

from reconcile.api.base import Reconcile

from .schema import (
    DataExtensionPropertyProposalResponse,
    DataExtensionQuery,
    DataExtensionQueryResponse,
    ReconciliationQueryBatch,
    ReconciliationQueryBatchForm,
    ReconciliationResult,
    ServiceSpec,
    SuggestResponse,
)

api = Router(tags=["Reconciliation (against all organisations)"])
reconcile = Reconcile()


@api.get(
    path="",
    response={200: ServiceSpec},
    exclude_none=True,
    summary="Service specification for reconciling against any nonprofit organisation",
    description="Get the service specification for reconciling against any nonprofit organisation",
)
def get_service_spec(request):
    return reconcile.get_service_spec(request, orgtypes="all")


@api.post(
    "",
    response={200: Dict[str, ReconciliationResult] | DataExtensionQueryResponse},
    exclude_none=True,
    summary="Reconciliation endpoint for reconciling against any nonprofit organisation",
    description="Reconciling queries against any nonprofit organisation.",
)
def reconcile_entities(
    request,
    queries: Form[ReconciliationQueryBatchForm],
):
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
def suggest_entity(request, prefix: str, cursor: int = 0):
    return reconcile.suggest_entity(request, prefix, cursor)


@api.get(
    "/extend/propose",
    response={200: DataExtensionPropertyProposalResponse},
    exclude_none=True,
)
def propose_properties(request, type: str, limit: int = 500):
    return reconcile.propose_properties(request, type_=type, limit=limit)


# @api.post(
#     "/extend",
#     response={200: DataExtensionQueryResponse},
#     exclude_none=True,
# )
# def data_extension(request, body: DataExtensionQuery):
#     return reconcile.data_extension(request, body)
