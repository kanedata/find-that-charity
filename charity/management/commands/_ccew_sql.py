UPDATE_CCEW = {}

UPDATE_CCEW['Insert into charity table'] = """
insert into charity_charity as cc (id, name, constitution , geographical_spread, address,
    postcode, phone, active, date_registered, date_removed, removal_reason, web, email,
    company_number, source, first_added, last_updated )
select CONCAT('GB-CHC-', c.regno) as "id",
    c.name as "name",
    c.gd as "constitution",
    c.aob as "geographical_spread",
    NULLIF(concat_ws(', ',
        c."add1",
        c."add2",
        c."add3",
        c."add4",
        c."add5"
    ), '') as "address",
    c.postcode as postcode,
    c.phone as "phone",
    c.orgtype = 'R' as active,
     to_date(reg.data->0->>'regdate', 'YYYY-MM-DD') as "date_registered",
    to_date(reg.data->-1->>'remdate', 'YYYY-MM-DD') as "date_removed",
    reg.data->-1->>'remcode' as "removal_reason",
    cm.web as "web",
    cm.email as "email",
    lpad(cm.coyno, 8, '0') as "company_number",
    '{source}' as "source",
    NOW() as "first_added",
    NOW() as "last_updated"
from charity_ccewcharity c
    left outer join charity_ccewmaincharity cm
        on c.regno = cm.regno
    left outer join (
        select regno,
            subno,
            jsonb_agg(cr order by regdate desc) as data
        from charity_ccewregistration cr
        group by regno, subno
    ) as reg
        on c.regno = reg.regno
            and c.subno = reg.subno
where c.subno = 0
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
    select CONCAT('GB-CHC-', c.regno) as org_id,
        c."fyend",
        c."fystart",
        c."income",
        c."expend" as "spending",
        'basic' as "account_type"
    from charity_ccewfinancial c
    where "income" is not null
) as a
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
    account_type = case when "cons_acc" = 'Yes' then 'consolidated' else 'charity' end
from charity_ccewpartb a
where cf.charity_id = CONCAT('GB-CHC-', a.regno)
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
select CONCAT('GB-CHC-', c.regno) as charity_id,
    aoo.id as "areaofoperation_id"
from charity_ccewcharityaoo c
    inner join charity_areaofoperation aoo
        on c.aookey = aoo.aookey
            and c.aootype = aoo.aootype
on conflict (charity_id, areaofoperation_id) do nothing;
"""

UPDATE_CCEW['Insert into charity names'] = """
insert into charity_charityname as cn (charity_id, name, "normalisedName", name_type)
select CONCAT('GB-CHC-', c.regno) as charity_id,
    c."name",
    c."name" as "normalisedName",
    case when c.subno != '0' then 'Subsidiary'
        when c.name = ccc."name" then 'Primary'
        else 'Alternative' end as "name_type"
from charity_ccewname c
    left outer join charity_ccewcharity ccc
        on c.regno = ccc.regno
            and c.subno = ccc.subno
on conflict (charity_id, name) do nothing;
"""

UPDATE_CCEW['Update charity objects'] = """
update charity_charity
set activities = "objects"
from (
    select CONCAT('GB-CHC-', a.regno) as charity_id,
        string_agg(regexp_replace("object", "next_seqno" || '$', ''), '' order by seqno) as "objects"
    from (
        select *,
            to_char(seqno::int + 1, 'fm0000') as "next_seqno"
        from charity_ccewobjects cc
        where cc.subno = '0'
    ) as a
    group by charity_id
) as a
where charity_charity.id = a.charity_id;
"""

UPDATE_CCEW['Insert into charity classification'] = """
insert into charity_charity_classification as ca (charity_id, vocabularyentries_id )
select org_id,
    ve.id
from (
    select CONCAT('GB-CHC-', c.regno) as org_id,
        c.class as "c_class"
    from charity_ccewclass c
) as c_class
    inner join charity_vocabularyentries ve
        on c_class.c_class = ve.code
    inner join charity_vocabulary v
        on ve.vocabulary_id = v.id
where v.title like 'ccew_%'
on conflict (charity_id, vocabularyentries_id) do nothing;
"""

UPDATE_CCEW['Insert into organisation table'] = r"""
insert into ftc_organisation (
    org_id, "orgIDs", linked_orgs, name, "alternateName",
    "charityNumber", "companyNumber", "streetAddress", "addressLocality",
    "addressRegion", "addressCountry", "postalCode",
    telephone, email, description, url, "latestIncome",
    "latestIncomeDate", "dateRegistered", "dateRemoved", active,
    status, parent, "dateModified", "organisationType", spider,
    location, org_id_scheme_id, "organisationTypePrimary_id",
    scrape_id, source_id
)
select cc.id as org_id,
    case when company_number in ('01234567', '12345678') then array[cc.id]
        when company_number is not null then array[cc.id, CONCAT('GB-COH-', company_number)]
        else array[cc.id] end as "orgIDs",
    case when company_number in ('01234567', '12345678') then array[cc.id]
        when company_number is not null then array[cc.id, CONCAT('GB-COH-', company_number)]
        else array[cc.id] end as "linked_orgs",
    cc.name,
    cn."alternateName" as "alternateName",
    regexp_replace(cc.id, 'GB\-(SC|NIC|COH|CHC)\-', '') as "charityNumber",
    cc.company_number as "companyNumber",
    concat_ws(', ', ccew.add1, ccew.add2) as "streetAddress",
    ccew.add3 as "addressLocality",
    ccew.add4 as "addressRegion",
    ccew.add5 as "addressCountry",
    cc.postcode as "postalCode",
    cc.phone as telephone,
    cc.email as email,
    cc.activities as description,
    cc.web as url,
    cc.income as "latestIncome",
    cc.latest_fye as "latestIncomeDate",
    cc.date_registered as "dateRegistered",
    cc.date_removed as "dateRemoved",
    cc.active,
    null as status,
    null as parent,
    now() as "dateModified",
    array['registered-charity'] ||
        case when cc."source" = 'ccew' then array['registered-charity-england-and-wales']
            when cc."source" = 'oscr' then array['registered-charity-scotland']
            when cc."source" = 'ccni' then array['registered-charity-northern-ireland']
            else array[]::text[] end ||
        case when cc.company_number is not null then array['registered-company', 'incorporated-charity']
            else array[]::text[] end ||
        case when cc.constitution ilike 'CIO - %' then array['charitable-incorporated-organisation', 'incorporated-charity']
            else array[]::text[] end ||
        case when cc.constitution ilike 'cio - association %' then array['charitable-incorporated-organisation-association']
            else array[]::text[] end ||
        case when cc.constitution ilike 'cio - foundation %' then array['charitable-incorporated-organisation-foundation']
            else array[]::text[] end
        as "organisationType",
    cc."source" as spider,
    l.location as "location",
    case when cc."source" = 'ccew' then 'GB-CHC'
        when cc."source" = 'oscr' then 'GB-SC'
        when cc."source" = 'ccni' then 'GB-NIC'
        else null end as "org_id_scheme_id",
    ot.slug as "organisationTypePrimary_id",
    {scrape_id} as scrape_id,
    cc."source" as source_id
from charity_charity cc
    left outer join (
        select charity_id,
            array_agg(name) as "alternateName"
        from charity_charityname
        group by charity_id
    ) as cn
        on cc.id = cn.charity_id
    left outer join charity_ccewcharity ccew
        on cc.id = CONCAT('GB-CHC-', ccew.regno)
            and ccew.subno = '0'
    left outer join (select charity_id,
            jsonb_agg(jsonb_build_object(
                'id', coalesce(ca."GSS", ca."ISO3166_1", ca."ContinentCode"),
                'name', aooname,
                'geoCode', coalesce(ca."GSS", ca."ISO3166_1", ca."ContinentCode")
            )) as "location"
        from charity_charity_areas_of_operation ccaoo
            inner join charity_areaofoperation ca
                on ccaoo.areaofoperation_id = ca.id
        group by charity_id) as l
    on l.charity_id = cc.id,
    ftc_organisationtype ot
where ot.title = 'Registered Charity'
    and cc.source = '{source}'
"""

UPDATE_CCEW['Insert into organisation link table'] = """
insert into "ftc_organisationlink" (
    org_id_a,
    org_id_b,
    spider,
    scrape_id,
    source_id
)
select cc.id as org_id_a,
    CONCAT('GB-COH-', company_number) as org_id_b,
    cc.source as spider,
    {scrape_id} as scrape_id,
    cc.source as source_id
from charity_charity cc
where company_number not in ('01234567', '12345678')
    and cc.source = '{source}'
"""
