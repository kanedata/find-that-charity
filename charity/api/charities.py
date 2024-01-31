from datetime import date as Date
from datetime import timedelta
from typing import Optional

from django.http import Http404
from django.shortcuts import get_list_or_404, get_object_or_404
from ninja import Router, Schema

from charity.models import Charity, CharityFinancial
from charity.utils import regno_to_orgid
from ftc.api.organisations import ResultError

from .schema import Charity as CharityOut
from .schema import CharityFinancial as CharityFinancialOut


class CharityResult(Schema):
    success: bool = True
    error: Optional[str] = None
    params: dict = {}
    result: Optional[CharityOut] = None


class CharityFinancialResult(Schema):
    success: bool = True
    error: Optional[str] = None
    params: dict = {}
    result: Optional[CharityFinancialOut] = None


api = Router(tags=["Charities"])


@api.get(
    "/{charity_id}",
    response={200: CharityResult, 404: ResultError},
)
def get_charity(request, charity_id: str):
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


@api.get(
    "/{charity_id}/financial/latest",
    response={200: CharityFinancialResult, 404: ResultError},
)
def get_charity_finance_latest(request, charity_id: str):
    charity_id = regno_to_orgid(charity_id)
    try:
        charity = get_object_or_404(Charity, id=charity_id)
        financial_years = get_list_or_404(CharityFinancial, charity=charity)
        financial_years = sorted(financial_years, key=lambda x: x.fyend, reverse=True)
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


@api.get(
    "/{charity_id}/financial/{date}",
    response={200: CharityFinancialResult, 404: ResultError},
)
def get_charity_finance_by_date(request, charity_id: str, date: Date):
    charity_id = regno_to_orgid(charity_id)
    try:
        charity = get_object_or_404(Charity, id=charity_id)

        # try using financial year start date
        financial_year = charity.financial.filter(
            fyend__gte=date,
            fystart__lte=date,
        ).first()

        # financial year end exact match
        if not financial_year:
            financial_year = charity.financial.filter(
                fyend=date,
            ).first()

        # financial year end is after or equal to the date
        if not financial_year:
            next_year = date + timedelta(days=365)
            financial_year = (
                charity.financial.filter(
                    fyend__gte=date,
                    fyend__lt=next_year,
                )
                .order_by("fyend")
                .first()
            )

        if not financial_year:
            raise Http404("No CharityFinancial matches the given query.")
        return {
            "error": None,
            "params": {
                "charity_id": charity_id,
                "date": date,
            },
            "result": financial_year,
        }
    except Http404 as e:
        return 404, {
            "error": str(e),
            "params": {"charity_id": charity_id, "date": date},
        }
