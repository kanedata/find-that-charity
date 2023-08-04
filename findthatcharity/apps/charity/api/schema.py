from datetime import date, datetime

from ninja import Schema


class Charity(Schema):
    id: str = None
    name: str = None
    constitution: str = None
    geographical_spread: str = None
    address: str = None
    postcode: str = None
    phone: str = None
    active: bool = None
    date_registered: date = None
    date_removed: date = None
    removal_reason: str = None
    web: str = None
    email: str = None
    company_number: str = None
    activities: str = None
    source: str = None
    first_added: datetime = None
    last_updated: datetime = None
    income: int = None
    spending: int = None
    latest_fye: date = None
    employees: int = None
    volunteers: int = None
    trustees: int = None
    dual_registered: bool = None


class CharityFinancial(Schema):
    fyend: date = None
    fystart: date = None
    income: int = None
    spending: int = None
    inc_leg: int = None
    inc_end: int = None
    inc_vol: int = None
    inc_fr: int = None
    inc_char: int = None
    inc_invest: int = None
    inc_other: int = None
    inc_total: int = None
    invest_gain: int = None
    asset_gain: int = None
    pension_gain: int = None
    exp_vol: int = None
    exp_trade: int = None
    exp_invest: int = None
    exp_grant: int = None
    exp_charble: int = None
    exp_gov: int = None
    exp_other: int = None
    exp_total: int = None
    exp_support: int = None
    exp_dep: int = None
    reserves: int = None
    asset_open: int = None
    asset_close: int = None
    fixed_assets: int = None
    open_assets: int = None
    invest_assets: int = None
    cash_assets: int = None
    current_assets: int = None
    credit_1: int = None
    credit_long: int = None
    pension_assets: int = None
    total_assets: int = None
    funds_end: int = None
    funds_restrict: int = None
    funds_unrestrict: int = None
    funds_total: int = None
    employees: int = None
    volunteers: int = None
    account_type: str = None
