UPDATE_OSCR = {}

UPDATE_OSCR["Insert into charity table"] = """
insert into charity_charity as cc (id, name, constitution , geographical_spread,
    address, postcode, phone, active, date_registered, date_removed, removal_reason,
    web, email, company_number, activities, source, first_added, last_updated, income,
    spending, latest_fye, dual_registered, scrape_id, spider)
select cc.org_id as org_id,
    cc.data->>'Charity Name' as "name",
    cc.data->>'Constitutional Form' as constitution,
    cc.data->>'Geographical Spread' as geographical_spread,
    cc.data->>'Principal Office/Trustees Address' as address,
    cc.data->>'Postcode' as postcode,
    null as phone,
    cc.data->>'Charity Status'!='Removed' as active,
    to_date(cc.data->>'Registered Date', 'YYYY-MM-DD') as date_registered,
    to_date(cc.data->>'Ceased Date', 'YYYY-MM-DD') as date_removed,
    null as removal_reason,
    cc.data->>'Website' as web,
    null as email,
    null as company_number,
    NULLIF(cc.data->>'Objectives', '-') as activities,
    cc.spider as source,
     NOW() as "first_added",
     NOW() as "last_updated",
    (cc.data->>'Most recent year income')::int as income,
    (cc.data->>'Most recent year expenditure')::int as spending,
    to_date(cc.data->>'Year End', 'YYYY-MM-DD') as latest_fye,
    null as dual_registered,
    cc.scrape_id as "scrape_id",
    cc.spider as "spider"
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
    source = EXCLUDED.source,
    first_added = cc.first_added,
    last_updated = EXCLUDED.last_updated,
    income = EXCLUDED.income,
    spending = EXCLUDED.spending,
    latest_fye = EXCLUDED.latest_fye,
    scrape_id = EXCLUDED.scrape_id,
    spider = EXCLUDED.spider;
"""

UPDATE_OSCR["Mark missing charities as inactive"] = """
update charity_charity as cc
set active = false
where spider = %(spider_name)s
    and scrape_id != %(scrape_id)s
"""

UPDATE_OSCR["Insert into charity financial"] = """
insert into charity_charityfinancial as cf (charity_id, fyend, income, inc_total,
    inc_other, inc_invest, inc_char, inc_vol, inc_fr, spending, exp_total, exp_vol,
    exp_charble, exp_other, account_type)
select cc.org_id as charity_id,
    to_date(cc.data->>'Year End', 'YYYY-MM-DD') as fyend,
    (cc.data->>'Most recent year income')::int as income,
    case when cc.data->>'Charitable activities spending' is not null
        then (cc.data->>'Most recent year income')::int else null end as inc_total,
    (cc.data->>'Other income')::int as inc_other,
    (cc.data->>'Investments income')::int as inc_invest,
    (cc.data->>'Charitable activities income')::int as inc_char,
    (cc.data->>'Donations and legacies income')::int as inc_vol,
    (cc.data->>'Other trading activities income')::int as inc_fr,
    (cc.data->>'Most recent year expenditure')::int as income,
    (cc.data->>'Charitable activities spending')::int +
        (cc.data->>'Raising funds spending')::int +
        (cc.data->>'Other spending')::int as exp_total,
    (cc.data->>'Raising funds spending')::int as exp_vol,
    (cc.data->>'Charitable activities spending')::int as exp_charble,
    (cc.data->>'Other spending')::int as exp_other,
    case when cc.data->>'Charitable activities spending' is not null
        then 'detailed_oscr' else 'basic_oscr' end as account_type
from charity_charityraw cc
where cc.spider = %(spider_name)s
    and cc.data->>'Year End' is not null
on conflict (charity_id, fyend) do update
set income = EXCLUDED.income,
    inc_total = EXCLUDED.inc_total,
    inc_other = EXCLUDED.inc_other,
    inc_invest = EXCLUDED.inc_invest,
    inc_char = EXCLUDED.inc_char,
    inc_vol = EXCLUDED.inc_vol,
    inc_fr = EXCLUDED.inc_fr,
    exp_total = EXCLUDED.exp_total,
    exp_vol = EXCLUDED.exp_vol,
    exp_charble = EXCLUDED.exp_charble,
    exp_other = EXCLUDED.exp_other,
    account_type = EXCLUDED.account_type;
"""

UPDATE_OSCR["Insert into charity names"] = """
insert into charity_charityname as cn (charity_id, name, "normalisedName", name_type)
select cc.org_id as org_id,
    cc.data->>'Charity Name' as "name",
    cc.data->>'Charity Name' as "normalisedName",
    'Registered name' as "name_type"
from charity_charityraw cc
where cc.spider = %(spider_name)s
union
select cc.org_id as org_id,
    cc.data->>'Known As' as "name",
    cc.data->>'Known As' as "normalisedName",
    'Known as' as "name_type"
from charity_charityraw cc
where cc.spider = %(spider_name)s and cc.data->>'Known As' is not null
on conflict (charity_id, name) do nothing;
"""

UPDATE_OSCR["Add dual registered flag"] = """
update charity_charity
set dual_registered = true
where id in (
    select org_id_a
    from ftc_organisationlink fo
    where fo.source_id = 'dual_registered'
)
and source = %(spider_name)s;
"""
