UPDATE_CCNI = {}

UPDATE_CCNI[
    "Insert into charity table"
] = """
insert into charity_charity as cc (id, name, constitution , geographical_spread,
    address, postcode, phone, active, date_registered, date_removed, removal_reason,
    web, email, company_number, activities, source, first_added, last_updated, income,
    spending, latest_fye, dual_registered, scrape_id, spider)
with address_rows as (
	select cc.reg_charity_number,
		jsonb_array_elements_text(array_to_json(regexp_split_to_array(cc.public_address, ', ?'))::jsonb - (-1)) as address_value
	from ccni_charity cc
),
address_groups as (
	select reg_charity_number, string_agg(address_value, ', ') as address
	from address_rows
	group by reg_charity_number
)
select 'GB-NIC-' || cc.reg_charity_number as org_id,
    cc.charity_name as "name",
    null as constitution,
    null as geographical_spread,
    address_groups.address as address,
    array_to_json(regexp_split_to_array(cc.public_address, ', ?'))::jsonb->>-1 as postcode,
    cc.telephone as phone,
    cc.status!='Removed' as active,
    cc.date_registered as date_registered,
    null as date_removed,
    null as removal_reason,
    cc.website as web,
    cc.email as email,
    case when cc.company_number != '0'
        then cc.company_number
        else null end as company_number,
    null as activities,
    %(spider_name)s as source,
     NOW() as "first_added",
     NOW() as "last_updated",
    cc.total_income as income,
    cc.total_spending as spending,
    cc.date_for_financial_year_ending as latest_fye,
    null as dual_registered,
    %(scrape_id)s as "scrape_id",
    %(spider_name)s as "spider"
from ccni_charity cc
	left outer join address_groups
		on cc.reg_charity_number = address_groups.reg_charity_number
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
insert into charity_charityfinancial as cf (
    charity_id, fyend, income, inc_total, spending,
    exp_total, exp_vol, exp_charble, account_type
)
select 'GB-NIC-' || cc.reg_charity_number as org_id,
    cc.date_for_financial_year_ending as fyend,
    cc.total_income as income,
    cc.total_income as inc_total,
    cc.total_spending as spending,
    cc.total_spending as exp_total,
    cc.income_generation_and_governance as exp_vol,
    cc.charitable_spending as exp_charble,
    case when cc.charitable_spending > 0
        then 'detailed_ccni' else 'basic_ccni' end as account_type
from ccni_charity cc
where cc.spider = %(spider_name)s
    and cc.date_for_financial_year_ending is not null
on conflict (charity_id, fyend) do update
set income = EXCLUDED.income,
    inc_total = EXCLUDED.inc_total,
    spending = EXCLUDED.spending,
    exp_total = EXCLUDED.exp_total,
    exp_vol = EXCLUDED.exp_vol,
    exp_charble = EXCLUDED.exp_charble,
    account_type = EXCLUDED.account_type;
"""
