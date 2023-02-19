from datetime import date

from django.http import Http404
from django.shortcuts import get_list_or_404, get_object_or_404
from ninja import Schema
from ninja_extra import api_controller, http_get

from charity.models import Charity, CharityFinancial
from charity.utils import regno_to_orgid
from ftc.api.organisations import ResultError

from .schema import Charity as CharityOut
from .schema import CharityFinancial as CharityFinancialOut


class CharityResult(Schema):
    success: bool = True
    error: str = None
    params: dict = {}
    result: CharityOut = None


class CharityFinancialResult(Schema):
    success: bool = True
    error: str = None
    params: dict = {}
    result: CharityFinancialOut = None


@api_controller(
    "/charities",
    tags=["Charities"],
)
class API:
    @http_get(
        "/{charity_id}",
        response={200: CharityResult, 404: ResultError},
    )
    def get_charity(self, request, charity_id: str):
        charity_id = regno_to_orgid(charity_id)
        try:
            return {
                "error": None,
                "params": {
                    "charity_id": charity_id,
                },
                "result": get_object_or_404(Charity, id=charity_id),
            }
        except Http404 as e:
            return 404, {
                "error": str(e),
                "params": {"charity_id": charity_id},
            }

    @http_get(
        "/{charity_id}/financial/latest",
        response={200: CharityFinancialResult, 404: ResultError},
    )
    def get_charity_finance_latest(self, request, charity_id: str):
        charity_id = regno_to_orgid(charity_id)
        try:
            charity = get_object_or_404(Charity, id=charity_id)
            financial_years = get_list_or_404(CharityFinancial, charity=charity)
            financial_years = sorted(
                financial_years, key=lambda x: x.fyend, reverse=True
            )
            return {
                "error": None,
                "params": {
                    "charity_id": charity_id,
                },
                "result": financial_years[0],
            }
        except Http404 as e:
            return 404, {
                "error": str(e),
                "params": {"charity_id": charity_id},
            }

    @http_get(
        "/{charity_id}/financial/{date}",
        response={200: CharityFinancialResult, 404: ResultError},
    )
    def get_charity_finance_by_date(self, request, charity_id: str, date: date):
        charity_id = regno_to_orgid(charity_id)
        try:
            charity = get_object_or_404(Charity, id=charity_id)
            financial_years = get_list_or_404(
                CharityFinancial,
                charity=charity,
                fyend__gte=date,
                fystart__lte=date,
            )
            return {
                "error": None,
                "params": {
                    "charity_id": charity_id,
                    "date": date,
                },
                "result": financial_years[0],
            }
        except Http404 as e:
            return 404, {
                "error": str(e),
                "params": {"charity_id": charity_id, "date": date},
            }
