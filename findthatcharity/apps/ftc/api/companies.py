from charity_django.companies.models import Company
from django.shortcuts import Http404
from ninja import Schema
from ninja_extra import api_controller, http_get

from findthatcharity.api.base import APIControllerBase, default_response
from findthatcharity.apps.ftc.api.schema import Company as CompanyOut


class CompanyResult(Schema):
    success: bool = True
    error: str = None
    params: dict = {}
    result: CompanyOut = None


@api_controller(
    "/companies",
    tags=["Companies"],
)
class API(APIControllerBase):
    @http_get(
        "/{company_number}",
        response={200: CompanyResult, **default_response},
    )
    def get_company(self, request, company_number: str):
        try:
            return {
                "error": None,
                "params": {
                    "company_number": company_number,
                },
                "result": Company.objects.get(CompanyNumber=company_number),
            }
        except Http404 as e:
            return 404, {
                "error": str(e),
                "params": {"company_number": company_number},
            }
