# Generated by Django 5.0.4 on 2024-11-13 16:25

from django.db import migrations

SQLQUERIES = {
    "superhighways_london_organisations": """
CREATE OR REPLACE VIEW superhighways_london_organisations AS
WITH n_charity AS (
    SELECT registered_charity_number,
        ARRAY_AGG(charity_name) AS also_known_as
    FROM charity_ccewcharityothernames
    GROUP BY 1
), t AS (
    SELECT organisation_number, count(*) AS latest_trustees
    FROM charity_ccewcharitytrustee cc 
    GROUP BY 1
), n_company AS (
    SELECT "CompanyNumber",
        ARRAY_AGG("CompanyName") AS also_known_as
    FROM companies_previousname
    GROUP BY 1
), main AS (
    SELECT 'GB-CHC-' || c.registered_charity_number AS organisation_id,
        c.registered_charity_number AS charity_number,
        c.charity_name AS organisation_name,
        'Registered Charity' AS organisation_type,
        c.charity_company_registration_number AS company_number,
        n_charity.also_known_as,
        c.charity_contact_postcode AS postcode,
        CASE WHEN c.charity_contact_web ILIKE 'http:%' THEN '' ELSE 'https://' END || c.charity_contact_web AS website,
        latest_income,
        latest_expenditure,
        pb.count_employees AS latest_employees,
        pa.count_volunteers AS latest_volunteers,
        t.latest_trustees,
        c.charity_registration_status AS registration_status,
        c.charity_reporting_status AS reporting_status,
        c.date_of_registration,
        c.date_of_removal,
        c.date_of_extract
    FROM charity_ccewcharity c
        LEFT OUTER JOIN n_charity ON c.registered_charity_number = n_charity.registered_charity_number
        LEFT OUTER JOIN charity_ccewcharityannualreturnhistory ar 
            ON ar.registered_charity_number = c.registered_charity_number
                AND ar.fin_period_end_date = c.latest_acc_fin_period_end_date 
        LEFT OUTER JOIN charity_ccewcharityarparta pa 
            ON pa.registered_charity_number = c.registered_charity_number
                AND pa.fin_period_end_date = c.latest_acc_fin_period_end_date 
        LEFT OUTER JOIN charity_ccewcharityarpartb pb 
            ON pb.registered_charity_number = c.registered_charity_number
                AND pb.fin_period_end_date = c.latest_acc_fin_period_end_date 
        LEFT OUTER JOIN t ON c.organisation_number = t.organisation_number
    WHERE c.linked_charity_number = 0
    UNION ALL
    SELECT 'GB-COH-' || c."CompanyNumber" AS organisation_id,
        NULL AS charity_number,
        c."CompanyName" AS organisation_name,
        'Community Interest Company' AS organisation_type,
        c."CompanyNumber" AS company_number,
        n_company.also_known_as,
        c."RegAddress_PostCode" AS postcode,
        NULL AS website,
        NULL AS latest_income,
        NULL AS latest_expenditure,
        NULL AS latest_employees,
        NULL AS latest_volunteers,
        NULL AS latest_trustees,
        c."CompanyStatus" AS registration_status,
        c."Accounts_AccountCategory" AS reporting_status,
        c."IncorporationDate" AS date_of_registration,
        c."DissolutionDate" AS date_of_removal,
        c.last_updated::date AS date_of_extract
    FROM companies_company c
        LEFT OUTER JOIN n_company ON n_company."CompanyNumber" = c."CompanyNumber" 
    WHERE "CompanyCategory" = 'community-interest-company'
), l AS (
    SELECT DISTINCT ON (l.org_id ) 
        l.org_id AS organisation_id,
        la."geoCode" AS la_code,
        la.name AS la_name,
        rgn."geoCode" AS rgn_code,
        rgn.name AS rgn_name,
        uk_ctry."geoCode" AS uk_ctry_code,
        uk_ctry.name AS uk_ctry_name,
        (rgn."geoCode" IS NOT NULL) AND (rgn."geoCode" = 'E12000007') AS london
    FROM ftc_organisationlocation l
        LEFT OUTER JOIN geo_geolookup la
            ON l.geo_laua = la."geoCode"
        LEFT OUTER JOIN geo_geolookup rgn
            ON l.geo_rgn= rgn."geoCode"
        LEFT OUTER JOIN geo_geolookup uk_ctry
            ON l.geo_ctry= uk_ctry."geoCode"
    WHERE (l.org_id ILIKE 'GB-CHC-%'
        OR l.org_id ILIKE 'GB-COH-%')
        AND l."locationType" = 'HQ'
    ORDER BY l.org_id
)
SELECT main.*,
    l.la_code AS hq_la_code,
    l.la_name AS hq_la_name,
    l.rgn_code AS hq_rgn_code,
    l.rgn_name AS hq_rgn_name,
    l.uk_ctry_code AS hq_ctry_code,
    l.uk_ctry_name AS hq_ctry_name,
    l.london AS hq_london
FROM main 
    LEFT OUTER JOIN l 
        ON main.organisation_id = l.organisation_id
WHERE l.london
    """,
    "superhighways_classification": """
CREATE OR REPLACE VIEW superhighways_classification AS
SELECT oc.org_id AS organisation_id,
    CASE WHEN oc.org_id ILIKE 'GB-CHC-%' THEN REPLACE(oc.org_id, 'GB-CHC-', '')::int ELSE NULL END AS charity_number,
    CASE WHEN oc.org_id ILIKE 'GB-COH-%' THEN REPLACE(oc.org_id, 'GB-COH-', '') ELSE NULL END AS company_number,
    v.title AS vocabulary,
    ve.code AS category_code,
    ve.title AS category_name
FROM ftc_vocabulary v
    INNER JOIN ftc_vocabularyentries ve
        ON v.id = ve.vocabulary_id 
    INNER JOIN ftc_organisationclassification oc
        ON ve.id = oc.vocabulary_id
WHERE oc.org_id ILIKE 'GB-CHC-%'
    OR  oc.org_id ILIKE 'GB-COH-%'
ORDER BY oc.org_id, v.title
""",
    "superhighways_area_of_operation": """
CREATE OR REPLACE VIEW superhighways_area_of_operation AS
SELECT l.org_id AS organisation_id,
    CASE WHEN l.org_id ILIKE 'GB-CHC-%' THEN REPLACE(l.org_id, 'GB-CHC-', '')::int ELSE NULL END AS charity_number,
    CASE WHEN l.org_id ILIKE 'GB-COH-%' THEN REPLACE(l.org_id, 'GB-COH-', '') ELSE NULL END AS company_number,
    l."locationType" AS location_type,
    la."geoCode" AS la_code,
    la.name AS la_name,
    rgn."geoCode" AS rgn_code,
    rgn.name AS rgn_name,
    uk_ctry."geoCode" AS uk_ctry_code,
    uk_ctry.name AS uk_ctry_name,
    ctry."geoCode" AS ctry_code,
    ctry.name AS ctry_name,
    (rgn."geoCode" IS NOT NULL) AND (rgn."geoCode" = 'E12000007') AS london
FROM ftc_organisationlocation l
    LEFT OUTER JOIN geo_geolookup la
        ON l.geo_laua = la."geoCode"
    LEFT OUTER JOIN geo_geolookup rgn
        ON l.geo_rgn= rgn."geoCode"
    LEFT OUTER JOIN geo_geolookup uk_ctry
        ON l.geo_ctry= uk_ctry."geoCode"
    LEFT OUTER JOIN geo_geolookup ctry
        ON l.geo_iso= ctry."geoCode"
WHERE l.org_id ILIKE 'GB-CHC-%'
    OR l.org_id ILIKE 'GB-COH-%'
ORDER BY l.org_id
""",
    "superhighways_trustees": """
CREATE OR REPLACE VIEW superhighways_trustees AS
SELECT 'GB-CHC-' || c.registered_charity_number AS organisation_id,
    c.registered_charity_number AS charity_number, 
    c.trustee_id
FROM charity_ccewcharitytrustee c
WHERE c.linked_charity_number = 0
""",
}


class Migration(migrations.Migration):
    dependencies = [
        ("ftc", "0034_update_charitydata"),
    ]

    operations = [
        migrations.RunSQL(
            sql=sql,
            reverse_sql=f"DROP VIEW IF EXISTS {name};",
        )
        for name, sql in SQLQUERIES.items()
    ]