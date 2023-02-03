from ninja_extra import NinjaExtraAPI

from charity.api import API as CharityAPI
from companies.api import API as CompanyAPI
from ftc.api import API as OrganisationAPI
from reconcile.api import API as ReconcileAPI

api = NinjaExtraAPI(
    title="Find that Charity API",
    description="Search for information about charities and other non-profit organisations",
    version="1.0",
)
api.register_controllers(OrganisationAPI)
api.register_controllers(CharityAPI)
api.register_controllers(CompanyAPI)
api.register_controllers(ReconcileAPI)
