from django.conf import settings
from ninja.errors import AuthenticationError
from ninja.security import APIKeyHeader
from ninja_apikey.security import check_apikey
from ninja_extra import NinjaExtraAPI

from findthatcharity.apps.charity.api import API as CharityAPI
from findthatcharity.apps.ftc.api import CompanyAPI, OrganisationAPI
from findthatcharity.apps.reconcile.api import API as ReconcileAPI


class FtcAuthentication(APIKeyHeader):
    param_name = "X-API-Key"

    def authenticate(self, request, key):
        if request.user.is_authenticated:
            return request.user

        allowed_hosts = request.META["ALLOWED_HOSTS"].split(";")
        for field in ["REMOTE_HOST", "REMOTE_ADDR"]:
            if request.META[field] in allowed_hosts:
                return request.META[field]

        user = check_apikey(key)

        if not user:
            return False

        request.user = user
        return user


limit = (
    settings.NINJA_EXTRA.get("THROTTLE_RATES", {})
    .get("anon", "10/minute")
    .replace("/", " per ")
)
api_description = f"""
Search for information about charities and other non-profit organisations

Responses are throttled to {limit} per IP address. You can request a higher 
limit by [contacting us](mailto:info@findthatcharity.uk).

This API is in development and may change without warning. Please contact us if 
you have any questions or suggestions.
"""

api = NinjaExtraAPI(
    title="Find that Charity API",
    description=api_description.strip(),
    version="1.0",
    # auth=[FtcAuthentication()],
    openapi_extra={
        "tags": [
            {
                "name": "Organisations",
                "description": "Search for information about charities and other non-profit organisations",
                "externalDocs": {
                    "url": "https://findthatcharity.uk/about/api/organisations/",
                },
            }
        ]
    },
)


@api.exception_handler(AuthenticationError)
def on_invalid_token(request, exc):
    return api.create_response(
        request, {"success": False, "error": "Unauthorised"}, status=401
    )


api.register_controllers(OrganisationAPI)
api.register_controllers(CharityAPI)
api.register_controllers(CompanyAPI)
api.register_controllers(ReconcileAPI)
