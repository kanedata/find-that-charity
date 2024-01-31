from ninja import NinjaAPI, Swagger

from charity.api import api as charity_api
from ftc.api import company_api, organisation_api
from reconcile.api import api as reconcile_api

api = NinjaAPI(
    title="Find that Charity API",
    description="Search for information about charities and other non-profit organisations",
    version="1.0",
    docs=Swagger(
        settings={
            "defaultModelsExpandDepth": 0,
        }
    ),
    openapi_extra={
        "tags": [
            {
                "name": "Organisations",
            },
            {
                "name": "Charities",
            },
            {
                "name": "Companies",
            },
            {
                "name": "Reconciliation (against all organisations)",
                "externalDocs": {
                    "description": "Reconciliation Service API v0.2",
                    "url": "https://reconciliation-api.github.io/specs/latest/",
                },
            },
            {
                "name": "Reconciliation (against registered companies)",
                "externalDocs": {
                    "description": "Reconciliation Service API v0.2",
                    "url": "https://reconciliation-api.github.io/specs/latest/",
                },
            },
            {
                "name": "Reconciliation (against specific type of organisation)",
                "externalDocs": {
                    "description": "Reconciliation Service API v0.2",
                    "url": "https://reconciliation-api.github.io/specs/latest/",
                },
            },
        ]
    },
)
api.add_router("/organisations", organisation_api)
api.add_router("/charities", charity_api)
api.add_router("/companies", company_api)
api.add_router("/reconcile", reconcile_api)
