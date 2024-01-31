from typing import Optional

from charity_django.companies.models import Company
from django.shortcuts import Http404, get_object_or_404
from ninja import Router, Schema

from ftc.api.organisations import ResultError
from ftc.api.schema import Company as CompanyOut


class CompanyResult(Schema):
    success: bool = True
    error: Optional[str] = None
    params: dict = {}
    result: Optional[CompanyOut] = None


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
            "result": get_object_or_404(Company, CompanyNumber=company_number),
        }
    except Http404 as e:
        return 404, {
            "error": str(e),
            "params": {"company_number": company_number},
        }
