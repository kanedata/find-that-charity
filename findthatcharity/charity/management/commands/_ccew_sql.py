UPDATE_CCEW = {}

UPDATE_CCEW['Insert into charity table'] = """
insert into charity_charity as cc (id, name, constitution , geographical_spread, address, 
	postcode, phone, active, date_registered, date_removed, removal_reason, web, email, 
    company_number, source, first_added, last_updated )
select c.org_id as "id",
	c.data->>'name' as "name",
	c.data->>'gd' as "constitution",
	c.data->>'aob' as "geographical_spread",
	NULLIF(concat_ws(', ', 
        c.data->>'add1',
        c.data->>'add2',
        c.data->>'add3',
        c.data->>'add4',
        c.data->>'add5'
     ), '') as "address",
	c.data->>'postcode' as "postcode",
	c.data->>'phone' as "phone",
	c.data->>'orgtype' = 'R' as "active",
 	to_date(c.data->'extract_registration'->0->>'regdate', 'YYYY-MM-DD') as "date_registered",
	to_date(c.data->'extract_registration'->-1->>'remdate', 'YYYY-MM-DD') as "date_removed",
	c.data->'extract_registration'->-1->>'remcode' as "removal_reason",
	c.data->>'web' as "web",
	c.data->>'email' as "email",
	c.data->>'coyno' as "company_number",
	-- c.data->>'' as "activities",
	c.spider as "source",
 	NOW() as "first_added",
 	NOW() as "last_updated"
	-- c.data->>'' as "income",
	-- c.data->>'' as "spending",
	-- c.data->>'' as "latest_fye",
	-- c.data->>'' as "dual_registered"
from charity_charityraw c
where c.spider = 'ccew'
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
    last_updated = EXCLUDED.last_updated;
"""

UPDATE_CCEW['Insert into charity financial'] = """
insert into charity_charityfinancial as cf (charity_id, fyend, fystart, income, spending, account_type)
select DISTINCT ON ("org_id", "fyend") a.*
from (
	select c.org_id,
		to_date(jsonb_array_elements(c.data->'extract_financial')->>'fyend', 'YYYY-MM-DD') as "fyend",
		to_date(jsonb_array_elements(c.data->'extract_financial')->>'fystart', 'YYYY-MM-DD') as "fystart",
		(jsonb_array_elements(c.data->'extract_financial')->>'income')::int as "income",
		(jsonb_array_elements(c.data->'extract_financial')->>'expend')::int as "spending",
		'basic' as "account_type"
	from charity_charityraw c
) as a
where "income" is not null
on conflict (charity_id, fyend) do update 
set fystart = EXCLUDED.fystart,
    income = EXCLUDED.income,
    spending = EXCLUDED.spending,
    account_type = cf.account_type;
"""

UPDATE_CCEW['Insert partb into charity financial'] = """
update charity_charityfinancial cf
set
    inc_leg = a.inc_leg,
    inc_end = a.inc_end,
    inc_vol = a.inc_vol,
    inc_fr = a.inc_fr,
    inc_char = a.inc_char,
    inc_invest = a.inc_invest,
    inc_other = a.inc_other,
    inc_total = a.inc_total,
    invest_gain = a.invest_gain,
    asset_gain = a.asset_gain,
    pension_gain = a.pension_gain,
    exp_vol = a.exp_vol,
    exp_trade = a.exp_trade,
    exp_invest = a.exp_invest,
    exp_grant = a.exp_grant,
    exp_charble = a.exp_charble,
    exp_gov = a.exp_gov,
    exp_other = a.exp_other,
    exp_total = a.exp_total,
    exp_support = a.exp_support,
    exp_dep = a.exp_dep,
    reserves = a.reserves,
    asset_open = a.asset_open,
    asset_close = a.asset_close,
    fixed_assets = a.fixed_assets,
    open_assets = a.open_assets,
    invest_assets = a.invest_assets,
    cash_assets = a.cash_assets,
    current_assets = a.current_assets,
    credit_1 = a.credit_1,
    credit_long = a.credit_long,
    pension_assets = a.pension_assets,
    total_assets = a.total_assets,
    funds_end = a.funds_end,
    funds_restrict = a.funds_restrict,
    funds_unrestrict = a.funds_unrestrict,
    funds_total = a.funds_total,
    employees = a.employees,
    volunteers = a.volunteers,
    account_type = case when "cons_acc" then 'consolidated' else 'charity' end 
from (
    select c.org_id,
        jsonb_array_elements(c.data->'extract_partb')->>'artype' as "artype",
        to_date(jsonb_array_elements(c.data->'extract_partb')->>'fyend', 'YYYY-MM-DD') as "fyend",
        to_date(jsonb_array_elements(c.data->'extract_partb')->>'fystart', 'YYYY-MM-DD') as "fystart",
        (jsonb_array_elements(c.data->'extract_partb')->>'inc_leg')::bigint as "inc_leg",
        (jsonb_array_elements(c.data->'extract_partb')->>'inc_end')::bigint as "inc_end",
        (jsonb_array_elements(c.data->'extract_partb')->>'inc_vol')::bigint as "inc_vol",
        (jsonb_array_elements(c.data->'extract_partb')->>'inc_fr')::bigint as "inc_fr",
        (jsonb_array_elements(c.data->'extract_partb')->>'inc_char')::bigint as "inc_char",
        (jsonb_array_elements(c.data->'extract_partb')->>'inc_invest')::bigint as "inc_invest",
        (jsonb_array_elements(c.data->'extract_partb')->>'inc_other')::bigint as "inc_other",
        (jsonb_array_elements(c.data->'extract_partb')->>'inc_total')::bigint as "inc_total",
        (jsonb_array_elements(c.data->'extract_partb')->>'invest_gain')::bigint as "invest_gain",
        (jsonb_array_elements(c.data->'extract_partb')->>'asset_gain')::bigint as "asset_gain",
        (jsonb_array_elements(c.data->'extract_partb')->>'pension_gain')::bigint as "pension_gain",
        (jsonb_array_elements(c.data->'extract_partb')->>'exp_vol')::bigint as "exp_vol",
        (jsonb_array_elements(c.data->'extract_partb')->>'exp_trade')::bigint as "exp_trade",
        (jsonb_array_elements(c.data->'extract_partb')->>'exp_invest')::bigint as "exp_invest",
        (jsonb_array_elements(c.data->'extract_partb')->>'exp_grant')::bigint as "exp_grant",
        (jsonb_array_elements(c.data->'extract_partb')->>'exp_charble')::bigint as "exp_charble",
        (jsonb_array_elements(c.data->'extract_partb')->>'exp_gov')::bigint as "exp_gov",
        (jsonb_array_elements(c.data->'extract_partb')->>'exp_other')::bigint as "exp_other",
        (jsonb_array_elements(c.data->'extract_partb')->>'exp_total')::bigint as "exp_total",
        (jsonb_array_elements(c.data->'extract_partb')->>'exp_support')::bigint as "exp_support",
        (jsonb_array_elements(c.data->'extract_partb')->>'exp_dep')::bigint as "exp_dep",
        (jsonb_array_elements(c.data->'extract_partb')->>'reserves')::bigint as "reserves",
        (jsonb_array_elements(c.data->'extract_partb')->>'asset_open')::bigint as "asset_open",
        (jsonb_array_elements(c.data->'extract_partb')->>'asset_close')::bigint as "asset_close",
        (jsonb_array_elements(c.data->'extract_partb')->>'fixed_assets')::bigint as "fixed_assets",
        (jsonb_array_elements(c.data->'extract_partb')->>'open_assets')::bigint as "open_assets",
        (jsonb_array_elements(c.data->'extract_partb')->>'invest_assets')::bigint as "invest_assets",
        (jsonb_array_elements(c.data->'extract_partb')->>'cash_assets')::bigint as "cash_assets",
        (jsonb_array_elements(c.data->'extract_partb')->>'current_assets')::bigint as "current_assets",
        (jsonb_array_elements(c.data->'extract_partb')->>'credit_1')::bigint as "credit_1",
        (jsonb_array_elements(c.data->'extract_partb')->>'credit_long')::bigint as "credit_long",
        (jsonb_array_elements(c.data->'extract_partb')->>'pension_assets')::bigint as "pension_assets",
        (jsonb_array_elements(c.data->'extract_partb')->>'total_assets')::bigint as "total_assets",
        (jsonb_array_elements(c.data->'extract_partb')->>'funds_end')::bigint as "funds_end",
        (jsonb_array_elements(c.data->'extract_partb')->>'funds_restrict')::bigint as "funds_restrict",
        (jsonb_array_elements(c.data->'extract_partb')->>'funds_unrestrict')::bigint as "funds_unrestrict",
        (jsonb_array_elements(c.data->'extract_partb')->>'funds_total')::bigint as "funds_total",
        (jsonb_array_elements(c.data->'extract_partb')->>'employees')::bigint as "employees",
        (jsonb_array_elements(c.data->'extract_partb')->>'volunteers')::bigint as "volunteers",
        jsonb_array_elements(c.data->'extract_partb')->>'cons_acc'='Yes' as "cons_acc",
        jsonb_array_elements(c.data->'extract_partb')->>'charity_acc'='Yes' as "charity_acc"
    from charity_charityraw c
) as a
where cf.charity_id = a.org_id
    and cf.fyend = a.fyend;
"""

UPDATE_CCEW['Update charity table with latest income'] = """
update charity_charity 
set latest_fye = cf.fyend,
	income = cf.income,
	spending = cf.spending
from (
	select charity_id, max(fyend) as max_fyend
	from charity_charityfinancial
	group by charity_id
) as cf_max
	inner join charity_charityfinancial cf
		on cf_max.charity_id = cf.charity_id 
			and cf_max.max_fyend = cf.fyend
where cf.charity_id = charity_charity.id;
"""

UPDATE_CCEW['Insert into charity areas of operation'] = """
insert into charity_charity_areas_of_operation as ca (charity_id, areaofoperation_id )
select aoo.org_id,
	aooref.id
from (
    select c.org_id,
        (jsonb_array_elements(c.data->'extract_charity_aoo')->>'aookey')::int as "aookey",
        jsonb_array_elements(c.data->'extract_charity_aoo')->>'aootype' as "aootype"
    from charity_charityraw c
    where c.spider = 'ccew'
) as aoo
	inner join charity_areaofoperation aooref
		on aoo.aookey = aooref.aookey 
			and aoo.aootype = aooref.aootype
on conflict (charity_id, areaofoperation_id) do nothing;
"""

UPDATE_CCEW['Insert into charity names'] = """
insert into charity_charityname as cn (charity_id, name, "normalisedName", name_type)
select a.org_id,
	"name",
	"name" as "normalisedName",
	case when "primary_name" = "name" then 'Primary'
		when "subno" = '0' then 'Alternative'
		else 'Subsidiary' end as "name_type"
from (
	select c.org_id,
		c.data->>'name' as "primary_name",
		jsonb_array_elements(c.data->'extract_name')->>'name' as "name",
		jsonb_array_elements(c.data->'extract_name')->>'subno' as "subno"
	from charity_charityraw c
    where c.spider = 'ccew'
) as a
on conflict (charity_id, name) do nothing;
"""

UPDATE_CCEW['Update charity objects'] = """
update charity_charity 
set activities = "objects"
from (
	select org_id,
		string_agg(regexp_replace("object", "seqno" || '$', ''), '' order by seqno) as "objects"
	from (
		select c.org_id,
			to_char((jsonb_array_elements(c.data->'extract_objects')->>'seqno')::int + 1, 'fm0000') as "seqno",
			jsonb_array_elements(c.data->'extract_objects')->>'object' as "object",
			jsonb_array_elements(c.data->'extract_objects')->>'subno' as "subno"
		from charity_charityraw c
        where c.spider = 'ccew'
	) as a
    where a.subno = '0'
	group by org_id
) as a
where charity_charity.id = a.org_id;
"""

UPDATE_CCEW['Insert into charity classification'] = """
insert into charity_charity_classification as ca (charity_id, vocabularyentries_id )
select org_id,
	ve.id
from (
select c.org_id,
	jsonb_array_elements(c.data->'extract_class')->>'class' as "c_class"
from charity_charityraw c
) as c_class
	inner join charity_vocabularyentries ve
		on c_class.c_class = ve.code 
	inner join charity_vocabulary v
		on ve.vocabulary_id = v.id 
where v.title like 'ccew_%'
on conflict (charity_id, vocabularyentries_id) do nothing;
"""
