from ninja import Router

from .reconcile_all import api as all_api
from .reconcile_company import api as company_api
from .reconcile_orgtype import api as orgtype_api

api = Router(tags=["Reconciliation"])
api.add_router("", all_api)
api.add_router("/company", company_api)
api.add_router("", orgtype_api)


__all__ = ["api"]
