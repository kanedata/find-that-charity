import json
from typing import Dict

from ninja import Form, Router

from reconcile.companies import COMPANY_RECON_TYPE, do_reconcile_query

from .base import Reconcile
from .schema import (
    ReconciliationQueryBatch,
    ReconciliationQueryBatchForm,
    ReconciliationResult,
    ServiceSpec,
)

api = Router(tags=["Reconciliation (against registered companies)"])


class CompanyReconcile(Reconcile):
    name = "Find that Charity Company Reconciliation API"
    view_url = "company_detail"
    view_url_args = {"company_number": "{{id}}"}
    suggest = False
    extend = False
    preview = False

    def reconcile_query(self, *args, **kwargs):
        return do_reconcile_query(*args, **kwargs)


reconcile = CompanyReconcile()


@api.get(
    "",
    response={200: ServiceSpec},
    exclude_none=True,
)
def get_company_service_spec(request):
    return reconcile.get_service_spec(request, defaultTypes=[COMPANY_RECON_TYPE])


@api.post(
    "",
    response={200: Dict[str, ReconciliationResult]},
    exclude_none=True,
    summary="Reconciliation endpoint for reconciling against registered companies",
    description="Reconciling queries against registered companies.",
)
def company_reconcile_entities(
    request,
    queries: Form[ReconciliationQueryBatchForm],
):
    queries_parsed = ReconciliationQueryBatch(queries=json.loads(queries.queries))
    return reconcile.reconcile(request, queries_parsed)
