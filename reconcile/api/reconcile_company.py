import json
from typing import Dict

from charity_django.companies.models import CompanyTypeChoices
from django.http import Http404
from ninja import Form, Query, Router

from ftc.documents import CompanyDocument
from reconcile.companies import COMPANY_RECON_TYPE, do_extend_query, do_reconcile_query
from reconcile.utils import convert_value

from .base import Reconcile
from .schema import (
    DataExtensionPropertyProposalQuery,
    DataExtensionPropertyProposalResponse,
    DataExtensionQuery,
    DataExtensionQueryResponse,
    ReconciliationQueryBatch,
    ReconciliationQueryBatchForm,
    ReconciliationResult,
    ServiceSpec,
    SuggestResponse,
    SuggestTypeQuery,
)

api = Router(tags=["Reconciliation (registered companies)"])


class CompanyReconcile(Reconcile):
    name = "Find that Charity Company Reconciliation API"
    view_url = "company_detail"
    view_url_args = {"company_number": "{{id}}"}
    suggest = ["property", "type"]
    extend = True
    preview = False
    base_type = "Company"

    def reconcile_query(self, *args, **kwargs):
        return do_reconcile_query(*args, **kwargs)

    def propose_properties(self, request, type_, limit=500):
        if type_ != self.base_type:
            msg = f"type must be {self.base_type}"
            raise Http404(msg)

        mapping = CompanyDocument._index.get_mapping()

        internal_fields = ["scrape", "spider", "id", "priority"]
        company_properties = [
            {"id": f, "name": f}
            for f in mapping["companies"]["mappings"]["properties"].keys()
            if f not in internal_fields
        ]

        return {"limit": limit, "type": type_, "properties": company_properties}

    def suggest_type(
        self,
        request,
        prefix: str,
        cursor: int = 0,
    ):
        if not prefix:
            raise Http404("Prefix must be supplied")

        results = [
            ("registered-company", "Registered Company")
        ] + CompanyTypeChoices.choices

        return {
            "result": [
                {
                    "id": id,
                    "name": name,
                    "notable": [],
                }
                for id, name in results
                if prefix.lower() in id.lower() or prefix.lower() in name.lower()
            ]
        }

    def data_extension(self, request, body: DataExtensionQuery) -> Dict:
        result = do_extend_query(
            ids=body.ids,
            properties=[p.__dict__ for p in body.properties],
        )
        rows = {}
        for row_id, row in result["rows"].items():
            rows[row_id] = {}
            for k, v in row.items():
                rows[row_id][k] = convert_value(v)

        return {
            "meta": result["meta"],
            "rows": rows,
        }


reconcile = CompanyReconcile()


@api.get(
    "",
    response={
        200: ServiceSpec | Dict[str, ReconciliationResult] | DataExtensionQueryResponse
    },
    exclude_none=True,
)
def get_company_service_spec(
    request,
    queries: Query[ReconciliationQueryBatchForm],
):
    if queries.queries:
        queries_parsed = ReconciliationQueryBatch(queries=json.loads(queries.queries))
        return {
            k: ReconciliationResult(**v)
            for k, v in reconcile.reconcile(request, queries_parsed).items()
        }
    elif queries.extend:
        queries_parsed = DataExtensionQuery(**json.loads(queries.extend))
        return DataExtensionQueryResponse(
            **reconcile.data_extension(request, queries_parsed)
        )
    return ServiceSpec(
        **reconcile.get_service_spec(request, defaultTypes=[COMPANY_RECON_TYPE])
    )


@api.post(
    "",
    response={200: Dict[str, ReconciliationResult] | DataExtensionQueryResponse},
    exclude_none=True,
    summary="Reconciliation endpoint for reconciling against registered companies",
    description="Reconciling queries against registered companies.",
)
def company_reconcile_entities(
    request,
    queries: Form[ReconciliationQueryBatchForm],
):
    if queries.queries:
        queries_parsed = ReconciliationQueryBatch(queries=json.loads(queries.queries))
        return {
            k: ReconciliationResult(**v)
            for k, v in reconcile.reconcile(request, queries_parsed).items()
        }
    elif queries.extend:
        queries_parsed = DataExtensionQuery(**json.loads(queries.extend))
        return DataExtensionQueryResponse(
            **reconcile.data_extension(request, queries_parsed)
        )


@api.get("/suggest/type", response={200: SuggestResponse}, exclude_none=True)
def company_suggest_type(request, query: Query[SuggestTypeQuery]):
    return reconcile.suggest_type(request, query.prefix, query.cursor)


@api.get("/suggest/property", response={200: SuggestResponse}, exclude_none=True)
def company_suggest_property(request, query: Query[SuggestTypeQuery]):
    return reconcile.suggest_property(request, query.prefix, query.cursor)


@api.get(
    "/extend/propose",
    response={200: DataExtensionPropertyProposalResponse},
    exclude_none=True,
)
def company_propose_properties(
    request, query: Query[DataExtensionPropertyProposalQuery]
):
    return reconcile.propose_properties(request, type_=query.type, limit=query.limit)
