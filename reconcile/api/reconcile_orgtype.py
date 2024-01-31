import json
from typing import Dict

from django.http import HttpResponse
from ninja import Form, Path, Router

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

api = Router(tags=["Reconciliation (against specific type of organisation)"])
reconcile = Reconcile()


@api.get(
    "/{orgtype}",
    response={200: ServiceSpec},
    exclude_none=True,
    tags=["Reconciliation (against specific type of organisation)"],
    summary="Service specification for reconciling against a specific type of organisation",
    description="Get the service specification for reconciling against a specific type of organisation",
)
def orgtype_get_service_spec(request, orgtype: str):
    return reconcile.get_service_spec(request, orgtypes=orgtype)


@api.post(
    "/{orgtype}",
    response={200: Dict[str, ReconciliationResult] | DataExtensionQueryResponse},
    exclude_none=True,
    tags=["Reconciliation (against specific type of organisation)"],
    summary="Reconciliation endpoint for reconciling against a specific type of organisation",
    description="Reconciling queries against a specific type of organisation. You can specify multiple types of organisation by separating them with a '+'.",
)
def orgtype_reconcile_entities(
    request,
    orgtype: Path[str],
    queries: Form[ReconciliationQueryBatchForm],
):
    if queries.queries:
        queries_parsed = ReconciliationQueryBatch(queries=json.loads(queries.queries))
        return reconcile.reconcile(request, queries_parsed, orgtypes=orgtype)
    elif queries.extend:
        queries_parsed = DataExtensionQuery(**json.loads(queries.extend))
        return reconcile.data_extension(request, queries_parsed)


@api.get(
    "/{orgtype}/preview",
    tags=["Reconciliation (against specific type of organisation)"],
    summary="HTML preview of an organisation",
)
def orgtype_preview(request, orgtype: str, id: str, response: HttpResponse):
    return reconcile.preview_view(request, id, response)


@api.get(
    "/{orgtype}/suggest/entity",
    response={200: SuggestResponse},
    exclude_none=True,
    tags=["Reconciliation (against specific type of organisation)"],
)
def orgtype_suggest_entity(request, orgtype: str, prefix: str, cursor: int = 0):
    return reconcile.suggest_entity(request, prefix, cursor, orgtypes=orgtype)


@api.get(
    "/{orgtype}/extend/propose",
    response={200: DataExtensionPropertyProposalResponse},
    exclude_none=True,
    tags=["Reconciliation (against specific type of organisation)"],
)
def orgtype_propose_properties(request, orgtype: str, type: str, limit: int = 500):
    return reconcile.propose_properties(request, type_=type, limit=limit)


@api.post(
    "/{orgtype}/extend",
    response={200: DataExtensionQueryResponse},
    exclude_none=True,
    tags=["Reconciliation (against specific type of organisation)"],
)
def orgtype_data_extension(request, orgtype: str, body: DataExtensionQuery):
    return reconcile.data_extension(request, body)
