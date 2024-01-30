from ninja import NinjaAPI

from charity.api import api as charity_api
from ftc.api import company_api, organisation_api
from reconcile.api import api as reconcile_api

api = NinjaAPI(
    title="Find that Charity API",
    description="Search for information about charities and other non-profit organisations",
    version="1.0",
)
api.add_router("/organisations", organisation_api)
api.add_router("/charities", charity_api)
api.add_router("/companies", company_api)
api.add_router("/reconcile", reconcile_api)
