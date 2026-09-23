from django.db import models
from django_db_views.db_view import DBMaterializedView


class TsgOrganisations(DBMaterializedView):
    org_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    postalCode = models.CharField(max_length=255, null=True)
    dateRegistered = models.DateField(null=True)
    age_years = models.IntegerField(null=True)
    dateRemoved = models.DateField(null=True)
    description = models.TextField(null=True)
    url = models.URLField(null=True)
    legal_form = models.CharField(max_length=255, null=True)
    data_source = models.CharField(max_length=255, null=True)
    latestIncomeDate = models.DateField(null=True)
    income = models.BigIntegerField(null=True)
    spending = models.BigIntegerField(null=True)
    latestEmployees = models.BigIntegerField(null=True)
    latestVolunteers = models.BigIntegerField(null=True)

    country = models.CharField(max_length=255, null=True)
    region = models.CharField(max_length=255, null=True)
    local_authority = models.CharField(max_length=255, null=True)
    local_authority_name = models.CharField(max_length=255, null=True)
    lsoa21 = models.CharField(max_length=255, null=True)
    geo_lat = models.CharField(max_length=255, null=True)
    geo_long = models.CharField(max_length=255, null=True)
    location_scope = models.CharField(max_length=255, null=True)
    ccew_what = models.CharField(max_length=255, null=True)
    ccew_who = models.CharField(max_length=255, null=True)
    ccew_how = models.CharField(max_length=255, null=True)
    ccew_charity_has_land = models.CharField(max_length=255, null=True)

    ccew_charity_name = models.CharField(max_length=255, null=True)
    ccew_charity_type = models.CharField(max_length=255, null=True)
    ccew_date_of_registration = models.DateField(null=True)
    ccew_date_of_removal = models.DateField(null=True)
    ccew_charity_reporting_status = models.CharField(max_length=255, null=True)
    ccew_charity_contact_postcode = models.CharField(max_length=255, null=True)
    ccew_charity_contact_web = models.URLField(max_length=255, null=True)
    ccew_charity_company_registration_number = models.CharField(
        max_length=255, null=True
    )
    ccew_charity_activities = models.TextField(null=True)

    ccew_alias_aliases = models.TextField(null=True)

    ccew_aoo = models.TextField(null=True)

    ccew_gd_governing_document_description = models.TextField(null=True)
    ccew_gd_charitable_objects = models.TextField(null=True)
    ccew_gd_area_of_benefit = models.TextField(null=True)

    ccew_pa_ar_due_date = models.DateField(null=True)
    ccew_pa_ar_received_date = models.DateField(null=True)
    ccew_pa_fin_period_start_date = models.DateField(null=True)
    ccew_pa_fin_period_end_date = models.DateField(null=True)
    ccew_pa_total_gross_income = models.BigIntegerField(null=True)
    ccew_pa_total_gross_expenditure = models.BigIntegerField(null=True)
    ccew_pa_count_govt_contracts = models.BigIntegerField(null=True)
    ccew_pa_count_govt_grants = models.BigIntegerField(null=True)
    ccew_pa_income_from_government_contracts = models.BigIntegerField(null=True)
    ccew_pa_income_from_government_grants = models.BigIntegerField(null=True)

    ccew_pb_income_donations_and_legacies = models.BigIntegerField(null=True)
    ccew_pb_income_charitable_activities = models.BigIntegerField(null=True)
    ccew_pb_income_other_trading_activities = models.BigIntegerField(null=True)
    ccew_pb_income_investments = models.BigIntegerField(null=True)
    ccew_pb_income_other = models.BigIntegerField(null=True)
    ccew_pb_income_total_income_and_endowments = models.BigIntegerField(null=True)
    ccew_pb_income_legacies = models.BigIntegerField(null=True)
    ccew_pb_income_endowments = models.BigIntegerField(null=True)
    ccew_pb_expenditure_raising_funds = models.BigIntegerField(null=True)
    ccew_pb_expenditure_charitable_expenditure = models.BigIntegerField(null=True)
    ccew_pb_expenditure_other = models.BigIntegerField(null=True)
    ccew_pb_expenditure_total = models.BigIntegerField(null=True)
    ccew_pb_expenditure_investment_management = models.BigIntegerField(null=True)
    ccew_pb_expenditure_grants_institution = models.BigIntegerField(null=True)
    ccew_pb_expenditure_governance = models.BigIntegerField(null=True)
    ccew_pb_expenditure_support_costs = models.BigIntegerField(null=True)
    ccew_pb_expenditure_depreciation = models.BigIntegerField(null=True)
    ccew_pb_gain_loss_investment = models.BigIntegerField(null=True)
    ccew_pb_gain_loss_pension_fund = models.BigIntegerField(null=True)
    ccew_pb_gain_loss_revaluation_fixed_investment = models.BigIntegerField(null=True)
    ccew_pb_gain_loss_other = models.BigIntegerField(null=True)
    ccew_pb_reserves = models.BigIntegerField(null=True)
    ccew_pb_assets_total_fixed = models.BigIntegerField(null=True)
    ccew_pb_assets_own_use = models.BigIntegerField(null=True)
    ccew_pb_assets_long_term_investment = models.BigIntegerField(null=True)
    ccew_pb_defined_benefit_pension_scheme = models.BigIntegerField(null=True)
    ccew_pb_assets_other_assets = models.BigIntegerField(null=True)
    ccew_pb_assets_total_liabilities = models.BigIntegerField(null=True)
    ccew_pb_assets_current_investment = models.BigIntegerField(null=True)
    ccew_pb_assets_total_assets_and_liabilities = models.BigIntegerField(null=True)
    ccew_pb_creditors_one_year_total_current = models.BigIntegerField(null=True)
    ccew_pb_creditors_falling_due_after_one_year = models.BigIntegerField(null=True)
    ccew_pb_assets_cash = models.BigIntegerField(null=True)
    ccew_pb_funds_endowment = models.BigIntegerField(null=True)
    ccew_pb_funds_unrestricted = models.BigIntegerField(null=True)
    ccew_pb_funds_restricted = models.BigIntegerField(null=True)
    ccew_pb_funds_total = models.BigIntegerField(null=True)
    ccew_pb_count_employees = models.BigIntegerField(null=True)
    ccew_pb_charity_only_accounts = models.BooleanField(null=True)
    ccew_pb_consolidated_account = models.BooleanField(null=True)

    class Meta:
        managed = False
        db_table = "tsg_organisation"

    view_definition = """
WITH l AS (
    SELECT org_id,
        STRING_AGG("geo_laua", ';') AS "local_authority",
        STRING_AGG("geo_rgn", ';') AS "region",
        STRING_AGG("geo_ctry", ';') AS "country",
        STRING_AGG("geo_lsoa21", ';') AS "lsoa21",
        MAX(l.geo_lat) AS geo_lat,
        MAX(l.geo_long) AS geo_long
    FROM ftc_organisationlocation l
    WHERE l."locationType" = 'HQ'
    GROUP BY 1
),
ls AS (
    SELECT c.org_id,
        string_agg(ve.title, ';') AS location_scope
    FROM ftc_organisationclassification c
        INNER JOIN ftc_vocabularyentries ve
            ON c.vocabulary_id = ve.id
        INNER JOIN ftc_vocabulary v
            ON ve.vocabulary_id = v.id
    WHERE v.slug = 'scale'
    GROUP BY 1
),
cc_c AS (
    SELECT 'GB-CHC-' || c.registered_charity_number AS org_id,
        STRING_AGG(c.classification_description, ';') FILTER (WHERE c.classification_type = 'What') AS ccew_what,
        STRING_AGG(c.classification_description, ';') FILTER (WHERE c.classification_type = 'Who') AS ccew_who,
        STRING_AGG(c.classification_description, ';') FILTER (WHERE c.classification_type = 'How') AS ccew_how
    FROM charity_ccewcharityclassification c
    GROUP BY 1
),
cc AS (
    SELECT 'GB-CHC-' || c.registered_charity_number AS org_id,
        c.charity_has_land,
        c.organisation_number, -- Added to facilitate joins with pa, pb, n, aoo, gd
        c.charity_name AS ccew_charity_name, -- Renamed to avoid conflict with o.name
        c.charity_type AS ccew_charity_type,
        c.date_of_registration AS ccew_date_of_registration,
        c.date_of_removal AS ccew_date_of_removal,
        c.charity_reporting_status AS ccew_charity_reporting_status,
        c.charity_contact_postcode AS ccew_charity_contact_postcode,
        c.charity_contact_web AS ccew_charity_contact_web,
        c.charity_company_registration_number AS ccew_charity_company_registration_number,
        c.charity_activities AS ccew_charity_activities,
        c.latest_acc_fin_period_end_date -- Added for pa and pb joins
    FROM charity_ccewcharity c
    WHERE c.linked_charity_number = 0
),
n AS (
    SELECT
        organisation_number,
        string_agg(charity_name, '; ') AS aliases
    FROM
        charity_ccewcharityothernames
    GROUP BY
        1
),
aoo AS (
    SELECT
        organisation_number,
        string_agg(geographic_area_description, '; ') AS aoo
    FROM
        charity_ccewcharityareaofoperation
    GROUP BY
        1
),
gd AS (
    SELECT
        organisation_number,
        governing_document_description,
        charitable_objects,
        area_of_benefit
    FROM
        charity_ccewcharitygoverningdocument
),
pa AS (
    SELECT
        organisation_number,
        ar_due_date,
        ar_received_date,
        fin_period_start_date,
        fin_period_end_date,
        total_gross_income,
        total_gross_expenditure,
        count_govt_contracts,
        count_govt_grants,
        income_from_government_contracts,
        income_from_government_grants
    FROM
        charity_ccewcharityarparta
),
pb AS (
    SELECT
        organisation_number,
        fin_period_end_date,
        income_donations_and_legacies,
        income_charitable_activities,
        income_other_trading_activities,
        income_investments,
        income_other,
        income_total_income_and_endowments,
        income_legacies,
        income_endowments,
        expenditure_raising_funds,
        expenditure_charitable_expenditure,
        expenditure_other,
        expenditure_total,
        expenditure_investment_management,
        expenditure_grants_institution,
        expenditure_governance,
        expenditure_support_costs,
        expenditure_depreciation,
        gain_loss_investment,
        gain_loss_pension_fund,
        gain_loss_revaluation_fixed_investment,
        gain_loss_other,
        reserves,
        assets_total_fixed,
        assets_own_use,
        assets_long_term_investment,
        defined_benefit_pension_scheme,
        assets_other_assets,
        assets_total_liabilities,
        assets_current_investment,
        assets_total_assets_and_liabilities,
        creditors_one_year_total_current,
        creditors_falling_due_after_one_year,
        assets_cash,
        funds_endowment,
        funds_unrestricted,
        funds_restricted,
        funds_total,
        count_employees,
        charity_only_accounts,
        consolidated_accounts
    FROM
        charity_ccewcharityarpartb
)
SELECT o.org_id,
    o."name",
    o."postalCode",
    o."dateRegistered",
    EXTRACT(YEAR FROM age(now(), o."dateRegistered")) AS age_years,
    o."dateRemoved",
    o."description",
    o."url",
    o."organisationTypePrimary_id" AS "legal_form",
    o."source_id" AS "data_source",
    o."latestIncomeDate",
    o."latestIncome" as income,
    o."latestSpending" as spending,
    o."latestEmployees",
    o."latestVolunteers",

    l."country",
    l."region",
    l.local_authority,
    la.name AS local_authority_name,
    l.lsoa21,
    l.geo_lat,
    l.geo_long,
    ls.location_scope,
    cc_c.ccew_what,
    cc_c.ccew_who,
    cc_c.ccew_how,
    cc.charity_has_land AS ccew_charity_has_land,

    cc.ccew_charity_name,
    cc.ccew_charity_type,
    cc.ccew_date_of_registration,
    cc.ccew_date_of_removal,
    cc.ccew_charity_reporting_status,
    cc.ccew_charity_contact_postcode,
    cc.ccew_charity_contact_web,
    cc.ccew_charity_company_registration_number,
    cc.ccew_charity_activities,

    n.aliases AS ccew_alias_aliases,

    aoo.aoo AS ccew_aoo,

    gd.governing_document_description AS ccew_gd_governing_document_description,
    gd.charitable_objects AS ccew_gd_charitable_objects,
    gd.area_of_benefit AS ccew_gd_area_of_benefit,

    pa.ar_due_date AS ccew_pa_ar_due_date,
    pa.ar_received_date AS ccew_pa_ar_received_date,
    pa.fin_period_start_date AS ccew_pa_fin_period_start_date,
    pa.fin_period_end_date AS ccew_pa_fin_period_end_date,
    pa.total_gross_income AS ccew_pa_total_gross_income,
    pa.total_gross_expenditure AS ccew_pa_total_gross_expenditure,
    pa.count_govt_contracts AS ccew_pa_count_govt_contracts,
    pa.count_govt_grants AS ccew_pa_count_govt_grants,
    pa.income_from_government_contracts AS ccew_pa_income_from_government_contracts,
    pa.income_from_government_grants AS ccew_pa_income_from_government_grants,

    pb.income_donations_and_legacies AS ccew_pb_income_donations_and_legacies,
    pb.income_charitable_activities AS ccew_pb_income_charitable_activities,
    pb.income_other_trading_activities AS ccew_pb_income_other_trading_activities,
    pb.income_investments AS ccew_pb_income_investments,
    pb.income_other AS ccew_pb_income_other,
    pb.income_total_income_and_endowments AS ccew_pb_income_total_income_and_endowments,
    pb.income_legacies AS ccew_pb_income_legacies,
    pb.income_endowments AS ccew_pb_income_endowments,
    pb.expenditure_raising_funds AS ccew_pb_expenditure_raising_funds,
    pb.expenditure_charitable_expenditure AS ccew_pb_expenditure_charitable_expenditure,
    pb.expenditure_other AS ccew_pb_expenditure_other,
    pb.expenditure_total AS ccew_pb_expenditure_total,
    pb.expenditure_investment_management AS ccew_pb_expenditure_investment_management,
    pb.expenditure_grants_institution AS ccew_pb_expenditure_grants_institution,
    pb.expenditure_governance AS ccew_pb_expenditure_governance,
    pb.expenditure_support_costs AS ccew_pb_expenditure_support_costs,
    pb.expenditure_depreciation AS ccew_pb_expenditure_depreciation,
    pb.gain_loss_investment AS ccew_pb_gain_loss_investment,
    pb.gain_loss_pension_fund AS ccew_pb_gain_loss_pension_fund,
    pb.gain_loss_revaluation_fixed_investment AS ccew_pb_gain_loss_revaluation_fixed_investment,
    pb.gain_loss_other AS ccew_pb_gain_loss_other,
    pb.reserves AS ccew_pb_reserves,
    pb.assets_total_fixed AS ccew_pb_assets_total_fixed,
    pb.assets_own_use AS ccew_pb_assets_own_use,
    pb.assets_long_term_investment AS ccew_pb_assets_long_term_investment,
    pb.defined_benefit_pension_scheme AS ccew_pb_defined_benefit_pension_scheme,
    pb.assets_other_assets AS ccew_pb_assets_other_assets,
    pb.assets_total_liabilities AS ccew_pb_assets_total_liabilities,
    pb.assets_current_investment AS ccew_pb_assets_current_investment,
    pb.assets_total_assets_and_liabilities AS ccew_pb_assets_total_assets_and_liabilities,
    pb.creditors_one_year_total_current AS ccew_pb_creditors_one_year_total_current,
    pb.creditors_falling_due_after_one_year AS ccew_pb_creditors_falling_due_after_one_year,
    pb.assets_cash AS ccew_pb_assets_cash,
    pb.funds_endowment AS ccew_pb_funds_endowment,
    pb.funds_unrestricted AS ccew_pb_funds_unrestricted,
    pb.funds_restricted AS ccew_pb_funds_restricted,
    pb.funds_total AS ccew_pb_funds_total,
    pb.count_employees AS ccew_pb_count_employees,
    pb.charity_only_accounts AS ccew_pb_charity_only_accounts,
    pb.consolidated_accounts AS ccew_pb_consolidated_accounts
FROM ftc_organisation o
    LEFT OUTER JOIN l
        ON o.org_id = l.org_id
    LEFT OUTER JOIN ls
        ON o.org_id = ls.org_id
    LEFT OUTER JOIN geo_geolookup la
        ON l.local_authority = la."geoCode"
    LEFT OUTER JOIN cc_c
        ON o.org_id = cc_c.org_id
    LEFT OUTER JOIN cc
        ON o.org_id = cc.org_id
    -- New Joins
    LEFT OUTER JOIN n
        ON cc.organisation_number = n.organisation_number
    LEFT OUTER JOIN aoo
        ON cc.organisation_number = aoo.organisation_number
    LEFT OUTER JOIN gd
        ON cc.organisation_number = gd.organisation_number
    LEFT OUTER JOIN pa
        ON cc.organisation_number = pa.organisation_number
        AND cc.latest_acc_fin_period_end_date = pa.fin_period_end_date
    LEFT OUTER JOIN pb
        ON cc.organisation_number = pb.organisation_number
        AND cc.latest_acc_fin_period_end_date = pb.fin_period_end_date
"""
