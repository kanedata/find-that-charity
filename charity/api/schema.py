from datetime import date, datetime
from typing import Optional

from ninja import Schema


class Charity(Schema):
    id: Optional[str] = None
    name: Optional[str] = None
    constitution: Optional[str] = None
    geographical_spread: Optional[str] = None
    address: Optional[str] = None
    postcode: Optional[str] = None
    phone: Optional[str] = None
    active: Optional[bool] = None
    date_registered: Optional[date] = None
    date_removed: Optional[date] = None
    removal_reason: Optional[str] = None
    web: Optional[str] = None
    email: Optional[str] = None
    company_number: Optional[str] = None
    activities: Optional[str] = None
    source: Optional[str] = None
    first_added: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    income: Optional[int] = None
    spending: Optional[int] = None
    latest_fye: Optional[date] = None
    employees: Optional[int] = None
    volunteers: Optional[int] = None
    trustees: Optional[int] = None
    dual_registered: Optional[bool] = None


class CharityFinancial(Schema):
    fyend: Optional[date] = None
    fystart: Optional[date] = None
    income: Optional[int] = None
    spending: Optional[int] = None
    inc_leg: Optional[int] = None
    inc_end: Optional[int] = None
    inc_vol: Optional[int] = None
    inc_fr: Optional[int] = None
    inc_char: Optional[int] = None
    inc_invest: Optional[int] = None
    inc_other: Optional[int] = None
    inc_total: Optional[int] = None
    invest_gain: Optional[int] = None
    asset_gain: Optional[int] = None
    pension_gain: Optional[int] = None
    exp_vol: Optional[int] = None
    exp_trade: Optional[int] = None
    exp_invest: Optional[int] = None
    exp_grant: Optional[int] = None
    exp_charble: Optional[int] = None
    exp_gov: Optional[int] = None
    exp_other: Optional[int] = None
    exp_total: Optional[int] = None
    exp_support: Optional[int] = None
    exp_dep: Optional[int] = None
    reserves: Optional[int] = None
    asset_open: Optional[int] = None
    asset_close: Optional[int] = None
    fixed_assets: Optional[int] = None
    open_assets: Optional[int] = None
    invest_assets: Optional[int] = None
    cash_assets: Optional[int] = None
    current_assets: Optional[int] = None
    credit_1: Optional[int] = None
    credit_long: Optional[int] = None
    pension_assets: Optional[int] = None
    total_assets: Optional[int] = None
    funds_end: Optional[int] = None
    funds_restrict: Optional[int] = None
    funds_unrestrict: Optional[int] = None
    funds_total: Optional[int] = None
    employees: Optional[int] = None
    volunteers: Optional[int] = None
    account_type: Optional[str] = None
