UPDATE_CCNI = {}

UPDATE_CCNI["Insert into charity table"] = """
insert into charity_charity as cc (id, name, constitution , geographical_spread,
    address, postcode, phone, active, date_registered, date_removed, removal_reason,
    web, email, company_number, activities, source, first_added, last_updated, income,
    spending, latest_fye, dual_registered, scrape_id, spider, employees, volunteers)
select cc.org_id as org_id,
    cc.data->>'Charity name' as "name",
    cc.data->>'Type of governing document' as constitution,
    null as geographical_spread,
    cc.data->>'address' as address,
    cc.data->>'postcode' as postcode,
    cc.data->>'Telephone' as phone,
    cc.data->>'Status'!='Removed' as active,
    to_date(cc.data->>'Date registered', 'YYYY-MM-DD') as date_registered,
    null as date_removed,
    null as removal_reason,
    cc.data->>'Website' as web,
    cc.data->>'Email' as email,
    case when cc.data->>'Company number' != '0'
        then cc.data->>'Company number'
        else null end as company_number,
    cc.data->>'Charitable purposes' as activities,
    cc.spider as source,
    NOW() as "first_added",
    NOW() as "last_updated",
    (cc.data->>'Total income')::int as income,
    (cc.data->>'Total spending')::int as spending,
    to_date(cc.data->>'Date for financial year ending', 'YYYY-MM-DD') as latest_fye,
    null as dual_registered,
    cc.scrape_id as "scrape_id",
    cc.spider as "spider",
    (cc.data->>'Employed staff')::int as employees,
    (cc.data->>'UK and Ireland volunteers')::int as volunteers
from charity_charityraw cc
where cc.spider = %(spider_name)s
on conflict (id) do update
set "name" = EXCLUDED.name,
    constitution = COALESCE(EXCLUDED.constitution, cc.constitution),
    geographical_spread = COALESCE(
        EXCLUDED.geographical_spread, cc.geographical_spread
    ),
    "address" = COALESCE(EXCLUDED.address, cc.address),
    postcode = COALESCE(EXCLUDED.postcode, cc.postcode),
    phone = COALESCE(EXCLUDED.phone, cc.phone),
    active = EXCLUDED.active,
    date_registered = EXCLUDED.date_registered,
    date_removed = EXCLUDED.date_removed,
    removal_reason = EXCLUDED.removal_reason,
    web = COALESCE(EXCLUDED.web, cc.web),
    email = COALESCE(EXCLUDED.email, cc.email),
    company_number = COALESCE(EXCLUDED.company_number, cc.company_number),
    activities = COALESCE(EXCLUDED.activities, cc.activities),
    source = EXCLUDED.source,
    first_added = cc.first_added,
    last_updated = EXCLUDED.last_updated,
    income = EXCLUDED.income,
    spending = EXCLUDED.spending,
    latest_fye = EXCLUDED.latest_fye,
    scrape_id = EXCLUDED.scrape_id,
    spider = EXCLUDED.spider,
    employees = EXCLUDED.employees,
    volunteers = EXCLUDED.volunteers;
"""

UPDATE_CCNI["Mark missing charities as inactive"] = """
update charity_charity as cc
set active = false
where spider = %(spider_name)s
    and scrape_id != %(scrape_id)s
"""

UPDATE_CCNI["Insert into charity financial"] = """
insert into charity_charityfinancial as cf (
    charity_id, fystart, fyend, income, inc_total, inc_vol, inc_char, inc_fr, inc_invest,
    inc_other, spending, exp_total, exp_vol, exp_charble, exp_gov, exp_other,
    total_assets, asset_close, account_type, employees, volunteers
)
select cc.org_id as org_id,
    to_date(cc.data->>'Financial period start', 'DD MONTH YYYY') as fystart,
    to_date(cc.data->>'Date for financial year ending', 'YYYY-MM-DD') as fyend,
    (cc.data->>'Total income')::int as income,
    case when (cc.data->>'Total income and endowments')::int > 0 then (cc.data->>'Total income and endowments')::int else null end as inc_total,
    case when (cc.data->>'Total income and endowments')::int > 0 then (cc.data->>'Income from donations and legacies')::int else null end as inc_vol,
    case when (cc.data->>'Total income and endowments')::int > 0 then (cc.data->>'Income from charitable activities')::int else null end as inc_char,
    case when (cc.data->>'Total income and endowments')::int > 0 then (cc.data->>'Income from other trading activities')::int else null end as inc_fr,
    case when (cc.data->>'Total income and endowments')::int > 0 then (cc.data->>'Income from investments')::int else null end as inc_invest,
    case when (cc.data->>'Total income and endowments')::int > 0 then (cc.data->>'Income from other')::int else null end as inc_other,
    (cc.data->>'Total spending')::int as spending,
    case when (cc.data->>'Total income and endowments')::int > 0 then (cc.data->>'Total expenditure')::int else null end as exp_total,
    case when (cc.data->>'Total income and endowments')::int > 0 then (cc.data->>'Expenditure on Raising funds')::int else null end as exp_vol,
    case when (cc.data->>'Total income and endowments')::int > 0 then (cc.data->>'Expenditure on Charitable activities')::int else null end as exp_charble,
    case when (cc.data->>'Total income and endowments')::int > 0 then (cc.data->>'Expenditure on Governance')::int else null end as exp_gov,
    case when (cc.data->>'Total income and endowments')::int > 0 then (cc.data->>'Expenditure on Other')::int else null end as exp_other,
    case when (cc.data->>'Total income and endowments')::int > 0 then (cc.data->>'Total net assets and liabilities')::int else null end as total_assets,
    case when (cc.data->>'Total income and endowments')::int > 0 then (cc.data->>'Assets and liabilities - Total fixed assets')::int else null end as asset_close,
    case when (cc.data->>'Total income and endowments')::int > 0
        then 'detailed_ccni' else 'basic_ccni' end as account_type,
    (cc.data->>'Employed staff')::int as employees,
    (cc.data->>'UK and Ireland volunteers')::int as volunteers
from charity_charityraw cc
where cc.spider = %(spider_name)s
    and cc.data->>'Date for financial year ending' is not null
on conflict (charity_id, fyend) do update
set fystart = EXCLUDED.fystart,
    income = EXCLUDED.income,
    inc_total = EXCLUDED.inc_total,
    inc_vol = EXCLUDED.inc_vol,
    inc_char = EXCLUDED.inc_char,
    inc_fr = EXCLUDED.inc_fr,
    inc_invest = EXCLUDED.inc_invest,
    inc_other = EXCLUDED.inc_other,
    spending = EXCLUDED.spending,
    exp_total = EXCLUDED.exp_total,
    exp_vol = EXCLUDED.exp_vol,
    exp_charble = EXCLUDED.exp_charble,
    exp_gov = EXCLUDED.exp_gov,
    exp_other = EXCLUDED.exp_other,
    total_assets = EXCLUDED.total_assets,
    asset_close = EXCLUDED.asset_close,
    account_type = EXCLUDED.account_type,
    employees = EXCLUDED.employees,
    volunteers = EXCLUDED.volunteers;
"""
