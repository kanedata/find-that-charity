UPDATE_CCNI = {}

UPDATE_CCNI[
    "Insert into charity table"
] = """
insert into charity_charity as cc (id, name, constitution , geographical_spread, address,
    postcode, phone, active, date_registered, date_removed, removal_reason, web, email,
    company_number, activities, source, first_added, last_updated, income, spending, latest_fye, 
    dual_registered, scrape_id, spider)
select cc.org_id as org_id,
    cc.data->>'Charity name' as "name",
    null as constitution,
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
    case when cc.data->>'Company Number' != '0' then cc.data->>'Company Number' else null end as company_number,
    null as activities,
    cc.spider as source,
     NOW() as "first_added",
     NOW() as "last_updated",
    (cc.data->>'Total income')::int as income,
    (cc.data->>'Total spending')::int as spending,
    to_date(cc.data->>'Date for financial year ending', 'YYYY-MM-DD') as latest_fye,
    null as dual_registered,
    cc.scrape_id as "scrape_id",
    cc.spider as "spider"
from charity_charityraw cc
where cc.spider = %(spider_name)s
on conflict (id) do update
set "name" = EXCLUDED.name,
    constitution = COALESCE(EXCLUDED.constitution, cc.constitution),
    geographical_spread = COALESCE(EXCLUDED.geographical_spread, cc.geographical_spread),
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

UPDATE_CCNI[
    "Mark missing charities as inactive"
] = """
update charity_charity as cc
set active = false
where spider = %(spider_name)s
    and scrape_id != %(scrape_id)s
"""

UPDATE_CCNI[
    "Insert into charity financial"
] = """
insert into charity_charityfinancial as cf (charity_id, fyend, income, inc_total, spending,
    exp_total, exp_vol, exp_charble, account_type)
select cc.org_id as org_id,
    to_date(cc.data->>'Date for financial year ending', 'YYYY-MM-DD') as fyend,
    (cc.data->>'Total income')::int as income,
    (cc.data->>'Total income')::int as inc_total,
    (cc.data->>'Total spending')::int as spending,
    (cc.data->>'Total spending')::int as exp_total,
    (cc.data->>'Income generation and governance')::int as exp_vol,
    (cc.data->>'Charitable spending')::int as exp_charble,
    case when (cc.data->>'Charitable spending')::int > 0 then 'detailed_ccni' else 'basic_ccni' end as account_type
from charity_charityraw cc
where cc.spider = %(spider_name)s
    and cc.data->>'Date for financial year ending' is not null
on conflict (charity_id, fyend) do update
set income = EXCLUDED.income,
    inc_total = EXCLUDED.inc_total,
    spending = EXCLUDED.spending,
    exp_total = EXCLUDED.exp_total,
    exp_vol = EXCLUDED.exp_vol,
    exp_charble = EXCLUDED.exp_charble,
    account_type = EXCLUDED.account_type;
"""
