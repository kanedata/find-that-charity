from charity_django.companies.models import Company
from django.shortcuts import Http404
from ninja import Router, Schema

from ftc.api.organisations import ResultError
from ftc.api.schema import Company as CompanyOut


class CompanyResult(Schema):
    success: bool = True
    error: str = None
    params: dict = {}
    result: CompanyOut = None


api = Router(tags=["Companies"])


@api.get(
    "/{company_number}",
    response={200: CompanyResult, 404: ResultError},
)
def get_company(request, company_number: str):
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
