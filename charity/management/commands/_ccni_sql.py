UPDATE_CCNI = {}

UPDATE_CCNI['Insert into charity table'] = """
insert into charity_charity as cc (id, name, constitution , geographical_spread, address,
    postcode, phone, active, date_registered, date_removed, removal_reason, web, email,
    company_number, activities, source, first_added, last_updated, income, spending, latest_fye, dual_registered)
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
    null as dual_registered
from charity_charityraw cc
where cc.spider = 'ccni'
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
    latest_fye = EXCLUDED.latest_fye;
"""

UPDATE_CCNI["Insert into charity financial"] = """
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
where cc.spider = 'ccni'
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


UPDATE_CCNI["Add vocabulary records"] = """
insert into charity_vocabulary (title, single)
select field, false
from (
    select cc.org_id as org_id,
        'ccni_purposes' as "field",
        unnest(string_to_array(replace(cc.data->>'What the charity does', ', ', '/'), ',')) as "value"
    from charity_charityraw cc
    where cc.spider = 'ccni'
    union
    select cc.org_id as org_id,
        'ccni_theme' as "field",
        unnest(string_to_array(replace(cc.data->>'How the charity works', ', ', '/'), ',')) as "value"
    from charity_charityraw cc
    where cc.spider = 'ccni'
    union
    select cc.org_id as org_id,
        'ccni_beneficiaries' as "field",
        unnest(string_to_array(replace(cc.data->>'Who the charity helps', ', ', '/'), ',')) as "value"
    from charity_charityraw cc
    where cc.spider = 'ccni'
) as a
group by field
on conflict (title) do nothing;
"""

UPDATE_CCNI["Add vocabulary entries"] = """
insert into charity_vocabularyentries (code, title, vocabulary_id)
select regexp_replace(lower(value), '[^a-z]+', '-', 'g'),  value, v.id
from (
    select field, value, count(*) as records
    from (
        select cc.org_id as org_id,
            'ccni_purposes' as "field",
            unnest(string_to_array(replace(cc.data->>'What the charity does', ', ', '/'), ',')) as "value"
        from charity_charityraw cc
        where cc.spider = 'ccni'
        union
        select cc.org_id as org_id,
            'ccni_theme' as "field",
            unnest(string_to_array(replace(cc.data->>'How the charity works', ', ', '/'), ',')) as "value"
        from charity_charityraw cc
        where cc.spider = 'ccni'
        union
        select cc.org_id as org_id,
            'ccni_beneficiaries' as "field",
            unnest(string_to_array(replace(cc.data->>'Who the charity helps', ', ', '/'), ',')) as "value"
        from charity_charityraw cc
        where cc.spider = 'ccni'
    ) as a
    group by field, value
) as b
    inner join charity_vocabulary v
        on b.field = v.title
order by id, records
on conflict (code, vocabulary_id) do nothing;
"""

UPDATE_CCNI["Add charity classification"] = """
insert into charity_charity_classification (charity_id, vocabularyentries_id)
select a.org_id as "charity_id",
    ve.id as "vocabularyentries_id"
from (
    select cc.org_id as org_id,
        'ccni_purposes' as "field",
        unnest(string_to_array(replace(cc.data->>'What the charity does', ', ', '/'), ',')) as "value"
    from charity_charityraw cc
    where cc.spider = 'ccni'
    union
    select cc.org_id as org_id,
        'ccni_theme' as "field",
        unnest(string_to_array(replace(cc.data->>'How the charity works', ', ', '/'), ',')) as "value"
    from charity_charityraw cc
    where cc.spider = 'ccni'
    union
    select cc.org_id as org_id,
        'ccni_beneficiaries' as "field",
        unnest(string_to_array(replace(cc.data->>'Who the charity helps', ', ', '/'), ',')) as "value"
    from charity_charityraw cc
    where cc.spider = 'ccni'
) as a
    left outer join charity_vocabulary v
        on a.field = v.title
    left outer join charity_vocabularyentries ve
        on a.value = ve.title and v.id = ve.vocabulary_id
on conflict (charity_id, vocabularyentries_id) do nothing;
"""
