UPDATE_CCEW = {}

UPDATE_CCEW[
    "Update archive addresses"
] = """
with addresses as (
select CONCAT('GB-CHC-', c.registered_charity_number) as "org_id",
    NULLIF(concat_ws(', ',
        c."charity_contact_address1",
        c."charity_contact_address2",
        c."charity_contact_address3",
        c."charity_contact_address4",
        c."charity_contact_address5"
    ), '') as address,
    c.charity_contact_postcode as postcode
from ccew_charity c
where linked_charity_number = 0
)
insert into charity_charityaddresshistory (
    org_id,
    address_md5,
    address,
    postcode,
    first_added,
    last_updated
)
select org_id,
    md5(lower(coalesce(address, '')::text ||
        coalesce(postcode, '')::text)) as address_md5,
    address,
    postcode,
    NOW() as first_added,
    NOW() as last_updated
from addresses
where address is not null or postcode is not null
on conflict (org_id, address_md5) do update
set first_added = charity_charityaddresshistory.first_added,
    last_updated = EXCLUDED.last_updated
"""

UPDATE_CCEW[
    "Insert into charity table"
] = """
insert into charity_charity as cc (id, name, constitution , geographical_spread,
    address, postcode, phone, active, date_registered, date_removed, removal_reason,
    web, email, company_number, activities, source, first_added, last_updated, income,
    spending, latest_fye, scrape_id, spider)
with earliest_event as (
    select e.organisation_number, min(e.date_of_event) as earliest_date
    from ccew_charityeventhistory e
    group by e.organisation_number
)
select distinct on(c.registered_charity_number)
    CONCAT('GB-CHC-', c.registered_charity_number) as "id",
    c.charity_name as "name",
    cgd.governing_document_description as "constitution",
    cgd.area_of_benefit as "geographical_spread",
    NULLIF(concat_ws(', ',
        c."charity_contact_address1",
        c."charity_contact_address2",
        c."charity_contact_address3",
        c."charity_contact_address4",
        c."charity_contact_address5"
    ), '') as "address",
    c.charity_contact_postcode as postcode,
    c.charity_contact_phone as "phone",
    c.charity_registration_status = 'Registered' as active,
    coalesce(ee.earliest_date, c.date_of_registration) as "date_registered",
    c.date_of_removal as "date_removed",
    ceh.reason as "removal_reason",
    c.charity_contact_web as "web",
    c.charity_contact_email as "email",
    lpad(c.charity_company_registration_number, 8, '0') as "company_number",
    coalesce(c.charity_activities, cgd.charitable_objects) as activities,
    %(source_id)s as "source",
    NOW() as "first_added",
    NOW() as "last_updated",
    c.latest_income as income,
    c.latest_expenditure as spending,
    c.latest_acc_fin_period_end_date as latest_fye,
    %(scrape_id)s as "scrape_id",
    %(spider_name)s as "spider"
from ccew_charity c
    left outer join ccew_charitygoverningdocument cgd
        on c.organisation_number = cgd.organisation_number
    left outer join ccew_charityeventhistory ceh
        on c.organisation_number = ceh.organisation_number
            and ceh.date_of_event = c.date_of_removal
            and ceh.event_type = 'Removed'
    left outer join earliest_event ee
        on c.organisation_number = ee.organisation_number
where c.linked_charity_number = 0
on conflict (id) do update
set "name" = EXCLUDED.name,
    constitution = COALESCE(EXCLUDED.constitution, cc.constitution),
    geographical_spread = COALESCE(
        EXCLUDED.geographical_spread,
        cc.geographical_spread
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
    income = COALESCE(EXCLUDED.income, cc.income),
    spending = COALESCE(EXCLUDED.spending, cc.spending),
    latest_fye = COALESCE(EXCLUDED.latest_fye, cc.latest_fye),
    scrape_id = EXCLUDED.scrape_id,
    spider = EXCLUDED.spider
"""

UPDATE_CCEW[
    "Add missing addresses"
] = """
update charity_charity c
set address = last_address.address,
    postcode = last_address.postcode
from (
    select distinct on (org_id) org_id, address, postcode
    from charity_charityaddresshistory cc
    order by org_id, last_updated desc
) as last_address
where last_address.org_id = c.id
    and c.address is null
    and c.postcode is null
"""

UPDATE_CCEW[
    "Mark missing charities as inactive"
] = """
update charity_charity as cc
set active = false
where spider = %(spider_name)s
    and scrape_id != %(scrape_id)s
"""

UPDATE_CCEW[
    "Insert annual return history into charity financial"
] = """
insert into charity_charityfinancial as cf (
    charity_id,
    fyend,
    fystart,
    income,
    spending,
    account_type
)
select DISTINCT ON ("org_id", "fyend") a.*
from (
    select CONCAT('GB-CHC-', c.registered_charity_number) as org_id,
        c.fin_period_end_date as "fyend",
        c.fin_period_start_date as "fystart",
        c.total_gross_income as "income",
        c.total_gross_expenditure as "spending",
        'basic' as "account_type"
    from ccew_charityannualreturnhistory c
    where "total_gross_income" is not null
) as a
on conflict (charity_id, fyend) do update
set fystart = EXCLUDED.fystart,
    income = EXCLUDED.income,
    spending = EXCLUDED.spending,
    account_type = cf.account_type;
"""

UPDATE_CCEW[
    "Insert parta into charity financial"
] = """
insert into charity_charityfinancial as cf (
    charity_id,
    fyend,
    fystart,
    income,
    spending,
    volunteers,
    account_type
)
select DISTINCT ON ("org_id", "fyend") a.*
from (
    select CONCAT('GB-CHC-', c.registered_charity_number) as org_id,
        c.fin_period_end_date as "fyend",
        c.fin_period_start_date as "fystart",
        c.total_gross_income as "income",
        c.total_gross_expenditure as "spending",
        c.count_volunteers as "volunteers",
        'basic' as "account_type"
    from ccew_charityarparta c
    where "total_gross_income" is not null
) as a
on conflict (charity_id, fyend) do update
set fystart = EXCLUDED.fystart,
    income = EXCLUDED.income,
    spending = EXCLUDED.spending,
    volunteers = EXCLUDED.volunteers,
    account_type = cf.account_type;
"""

UPDATE_CCEW[
    "Insert partb into charity financial"
] = """
update charity_charityfinancial cf
set
    inc_leg = a.income_legacies,
    inc_end = a.income_endowments,
    inc_vol = a.income_donations_and_legacies,
    inc_fr = a.income_other_trading_activities,
    inc_char = a.income_charitable_activities,
    inc_invest = a.income_investments,
    inc_other = a.income_other,
    inc_total = a.income_total_income_and_endowments,
    invest_gain = a.gain_loss_investment,
    asset_gain = a.gain_loss_pension_fund,
    pension_gain = a.gain_loss_pension_fund,
    exp_vol = a.expenditure_raising_funds,
    exp_trade = null,
    exp_invest = a.expenditure_investment_management,
    exp_grant = a.expenditure_grants_institution,
    exp_charble = a.expenditure_charitable_expenditure,
    exp_gov = a.expenditure_governance,
    exp_other = a.expenditure_other,
    exp_total = a.expenditure_total,
    exp_support = a.expenditure_support_costs,
    exp_dep = a.expenditure_depreciation,
    reserves = a.reserves,
    asset_open = null,
    asset_close = a.assets_total_fixed, -- Total fixed assets
    fixed_assets = a.assets_long_term_investment, -- Fixed Investments Assets
    open_assets = null,
    invest_assets = a.assets_current_investment, -- Current Investment Assets
    cash_assets = a.assets_cash, -- Cash
    current_assets = null, -- Total Current Assets
    credit_1 = a.creditors_one_year_total_current,
    credit_long = a.creditors_falling_due_after_one_year,
    pension_assets = a.defined_benefit_pension_scheme,
    total_assets = a.assets_total_assets_and_liabilities,
    funds_end = a.funds_endowment,
    funds_restrict = a.funds_restricted,
    funds_unrestrict = a.funds_unrestricted,
    funds_total = a.funds_total,
    employees = a.count_employees,
    account_type = case when "consolidated_accounts"
        then 'consolidated' else 'charity' end
from ccew_charityarpartb a
where cf.charity_id = CONCAT('GB-CHC-', a.registered_charity_number)
    and cf.fyend = a.fin_period_end_date;
"""

UPDATE_CCEW[
    "Update number of employees and volunteers"
] = """
update charity_charity
set employees = cf.employees,
    volunteers = cf.volunteers
from charity_charityfinancial cf
where charity_charity.id = cf.charity_id
    and charity_charity.latest_fye = cf.fyend;
"""

UPDATE_CCEW[
    "Update number of trustees"
] = """
update charity_charity
set trustees = t.trustees
from (
    select CONCAT('GB-CHC-', registered_charity_number) as "charity_id",
        COUNT(*) as trustees
    from ccew_charitytrustee
    where linked_charity_number = 0
    group by charity_id
) as t
where charity_charity.id = t.charity_id;
"""

UPDATE_CCEW[
    "Insert into charity areas of operation"
] = """
insert into charity_charity_areas_of_operation as ca (charity_id, areaofoperation_id )
select CONCAT('GB-CHC-', c.registered_charity_number) as charity_id,
    aoo.id as "areaofoperation_id"
from ccew_charityareaofoperation c
    inner join charity_areaofoperation aoo
        on c.geographic_area_description = aoo.aooname
on conflict (charity_id, areaofoperation_id) do nothing;
"""

UPDATE_CCEW[
    "Insert into charity names"
] = """
insert into charity_charityname as cn (charity_id, name, "normalisedName", name_type)
select CONCAT('GB-CHC-', c.registered_charity_number) as charity_id,
    c.charity_name as "name",
    c.charity_name as "normalisedName",
    case when c.linked_charity_number != '0' then 'Subsidiary'
        when c.charity_name = ccc."charity_name" then 'Primary'
        else c.charity_name_type end as "name_type"
from ccew_charityothernames c
    left outer join ccew_charity ccc
        on c.registered_charity_number = ccc.registered_charity_number
            and c.linked_charity_number = ccc.linked_charity_number
where c.charity_name is not null
on conflict (charity_id, name) do nothing;
"""

UPDATE_CCEW[
    "Update charity classification to set current as false"
] = """
update ftc_vocabularyentries
set current = false
where vocabulary_id in (
    select id from ftc_vocabulary where slug in (
        'ccew_theme',
        'ccew_activities',
        'ccew_beneficiaries'
    )
);
"""

UPDATE_CCEW[
    "Insert charity classification into vocabs"
] = """
insert into ftc_vocabularyentries (code, title, vocabulary_id, current)
select c.classification_code as "code",
    c.classification_description as "title",
    cv.id,
    true
from ccew_charityclassification c
    inner join ftc_vocabulary cv
        on case when c.classification_type = 'What' then 'ccew_theme'
            when c.classification_type = 'How' then 'ccew_activities'
            when c.classification_type = 'Who' then 'ccew_beneficiaries'
            else null end = cv.slug
group by c.classification_code,
    c.classification_description,
    cv.id
on conflict (code, vocabulary_id) do update
set title = EXCLUDED.title, current = true;
"""

UPDATE_CCEW[
    "Insert into charity classification"
] = """
insert into ftc_organisationclassification as ca (
    org_id,
    spider,
    scrape_id,
    source_id,
    vocabulary_id
)
select org_id,
    %(spider_name)s as "spider",
    %(scrape_id)s as "scrape_id",
    %(source_id)s as "source_id",
    ve.id
from (
    select CONCAT('GB-CHC-', c.registered_charity_number) as org_id,
        cast(c.classification_code as varchar) as "c_class"
    from ccew_charityclassification c
) as c_class
    inner join ftc_vocabularyentries ve
        on c_class.c_class = ve.code
    inner join ftc_vocabulary v
        on ve.vocabulary_id = v.id
where v.slug like 'ccew_%%';
"""

UPDATE_CCEW[
    "Insert into organisation table"
] = r"""
insert into ftc_organisation (
    org_id, "orgIDs", linked_orgs, name, "alternateName",
    "charityNumber", "companyNumber", "streetAddress", "addressLocality",
    "addressRegion", "addressCountry", "postalCode",
    telephone, email, description, url, "latestIncome",
    "latestSpending", "latestEmployees", "latestVolunteers", "trusteeCount",
    "latestIncomeDate", "dateRegistered", "dateRemoved", active,
    status, parent, "dateModified", "organisationType", spider,
    org_id_scheme_id, "organisationTypePrimary_id",
    scrape_id, source_id
)
select distinct on (cc.id)
    cc.id as org_id,
    case when company_number in ('01234567', '12345678', '00000000') then array[cc.id]
        when company_number is not null then array[
            cc.id,
            CONCAT('GB-COH-', company_number)
        ]
        else array[cc.id] end as "orgIDs",
    case when company_number in ('01234567', '12345678', '00000000') then array[cc.id]
        when company_number is not null then array[
            cc.id,
            CONCAT('GB-COH-', company_number)
        ]
        else array[cc.id] end as "linked_orgs",
    cc.name,
    cn."alternateName" as "alternateName",
    regexp_replace(cc.id, 'GB\-(SC|NIC|COH|CHC)\-', '') as "charityNumber",
    cc.company_number as "companyNumber",
    concat_ws(
        ', ',
        ccew.charity_contact_address1,
        ccew.charity_contact_address2
    ) as "streetAddress",
    ccew.charity_contact_address3 as "addressLocality",
    ccew.charity_contact_address4 as "addressRegion",
    ccew.charity_contact_address5 as "addressCountry",
    cc.postcode as "postalCode",
    cc.phone as telephone,
    cc.email as email,
    cc.activities as description,
    cc.web as url,
    cc.income as "latestIncome",
    cc.spending as "latestSpending",
    cc.employees as "latestEmployees",
    cc.volunteers as "latestVolunteers",
    cc.trustees as "trusteeCount",
    cc.latest_fye as "latestIncomeDate",
    cc.date_registered as "dateRegistered",
    cc.date_removed as "dateRemoved",
    cc.active,
    null as status,
    null as parent,
    now() as "dateModified",
    array['registered-charity'] ||
        case when cc."source" = 'ccew' then array[
                'registered-charity-england-and-wales'
            ]
            when cc."source" = 'oscr' then array[
                'registered-charity-scotland'
            ]
            when cc."source" = 'ccni' then array[
                'registered-charity-northern-ireland'
            ]
            else array[]::text[] end ||
        case when cc.company_number is not null
                or ccew.charity_type = 'Charitable company'
            then array['registered-company', 'incorporated-charity']
            else array[]::text[] end ||
        case when cc.constitution ilike 'CIO - %%'
                or ccew.charity_type = 'CIO'
            then array['charitable-incorporated-organisation', 'incorporated-charity']
            else array[]::text[] end ||
        case when cc.constitution ilike 'cio - association %%'
            then array['charitable-incorporated-organisation-association']
            else array[]::text[] end ||
        case when cc.constitution ilike 'cio - foundation %%'
            then array['charitable-incorporated-organisation-foundation']
            else array[]::text[] end ||
        case when ccew.charity_type = 'Trust' then array['trust']
            else array[]::text[] end
        as "organisationType",
    cc."source" as spider,
    case when cc."source" = 'ccew' then 'GB-CHC'
        when cc."source" = 'oscr' then 'GB-SC'
        when cc."source" = 'ccni' then 'GB-NIC'
        else null end as "org_id_scheme_id",
    ot.slug as "organisationTypePrimary_id",
    %(scrape_id)s as scrape_id,
    cc."source" as source_id
from charity_charity cc
    left outer join (
        select charity_id,
            array_agg(distinct name) as "alternateName"
        from charity_charityname
        group by charity_id
    ) as cn
        on cc.id = cn.charity_id
    left outer join ccew_charity ccew
        on cc.id = CONCAT('GB-CHC-', ccew.registered_charity_number)
            and ccew.linked_charity_number = '0',
    ftc_organisationtype ot
where ot.title = 'Registered Charity'
    and cc.source = %(source_id)s
"""

UPDATE_CCEW[
    "Insert companies into organisation link table"
] = """
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
    %(scrape_id)s as scrape_id,
    cc.source as source_id
from charity_charity cc
where company_number not in ('01234567', '12345678', '00000000')
    and cc.source = %(source_id)s
"""

UPDATE_CCEW[
    "Insert into organisation location table"
] = """
insert into ftc_organisationlocation (
    org_id,
    name,
    "geoCode",
    "geoCodeType",
    "locationType",
    geo_iso,
    "spider",
    "source_id",
    "scrape_id"
)
select CONCAT('GB-CHC-', cc.registered_charity_number) as org_id,
    aooname as name,
    coalesce(ca."GSS", ca."ISO3166_1") as "geoCode",
    case when ca."GSS" is not null then 'ONS'
         when ca."ISO3166_1" is not null then 'ISO'
         else null end as "geoCodeType",
    'AOO' as "locationType",
    ca."ISO3166_1" as geo_iso,
    %(source_id)s as spider,
    %(source_id)s as source_id,
    %(scrape_id)s as scrape_id
from ccew_charityareaofoperation cc
    inner join charity_areaofoperation ca
        on cc.geographic_area_description = ca.aooname
where ca."GSS" is not null or ca."ISO3166_1" is not null
on conflict (
    "org_id",
    "name",
    "geoCodeType",
    "locationType",
    "spider",
    "source_id",
    "scrape_id"
) do nothing;
"""
