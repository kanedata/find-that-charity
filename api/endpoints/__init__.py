from ninja import NinjaAPI

from .organisation import organisation_router
from reconcile.api.endpoints import reconcile_router

api = NinjaAPI(
    title="Find that Charity API",
    description="Search for information about charities and other non-profit organisations",
    version="1.0",
)

api.add_router("/organisation/", organisation_router, tags=["Organisations"])
api.add_router("/reconcile/", reconcile_router, tags=["Reconciliation"])
