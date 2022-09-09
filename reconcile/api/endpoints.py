from typing import Dict
from ninja import Router, Query

from reconcile.api.schema import ReconciliationResultBatch, ReconciliationQuery

reconcile_router = Router()


@reconcile_router.post(
    "/",
    response={200: ReconciliationResultBatch},
)
def reconcile(request, queries: Dict[str, ReconciliationQuery] = Query({})):
    pass
