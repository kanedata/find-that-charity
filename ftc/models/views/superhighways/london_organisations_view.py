from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_db_views.db_view import DBMaterializedView


class SuperhighwaysLondonOrganisationsView(DBMaterializedView):
    organisation_id = models.CharField(max_length=255)
    charity_number = models.IntegerField(null=True)
    organisation_name = models.CharField(max_length=255)
    organisation_type = models.CharField(max_length=255)
    company_number = models.CharField(max_length=255, null=True)
    also_known_as = ArrayField(models.CharField(max_length=255), null=True)
    postcode = models.CharField(max_length=255, null=True)
    website = models.CharField(max_length=255, null=True)
    latest_income = models.BigIntegerField(null=True)
    latest_expenditure = models.BigIntegerField(null=True)
    latest_employees = models.BigIntegerField(null=True)
    latest_volunteers = models.BigIntegerField(null=True)
    latest_trustees = models.BigIntegerField(null=True)
    registration_status = models.CharField(max_length=255, null=True)
    reporting_status = models.CharField(max_length=255, null=True)
    date_of_registration = models.DateField(null=True)
    date_of_removal = models.DateField(null=True)
    date_of_extract = models.DateField(null=True)
    hq_la_code = models.CharField(max_length=200, null=True)
    hq_la_name = models.CharField(max_length=255, null=True)
    hq_rgn_code = models.CharField(max_length=200, null=True)
    hq_rgn_name = models.CharField(max_length=255, null=True)
    hq_ctry_code = models.CharField(max_length=200, null=True)
    hq_ctry_name = models.CharField(max_length=255, null=True)
    hq_london = models.BooleanField(null=True)
    hq_ward_code = models.CharField(max_length=200, null=True)
    hq_ward_name = models.CharField(max_length=255, null=True)
    charity_activities = models.TextField(null=True)
    any_london = models.BooleanField(null=True)
    cqc_category = models.CharField(max_length=255, null=True)
    charity_has_land = models.BooleanField(null=True)
    charity_is_cio = models.BooleanField(null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    class Meta:
        managed = False
        db_table = "superhighways_london_organisations_view"

    view_definition = """
WITH n_charity AS (
    SELECT registered_charity_number,
        ARRAY_AGG(charity_name) AS also_known_as
    FROM charity_ccewcharityothernames
    GROUP BY 1
), t AS (
    SELECT organisation_number, count(*) AS latest_trustees
    FROM charity_ccewcharitytrustee cc 
    GROUP BY 1
), main AS (
    SELECT 'GB-CHC-' || c.registered_charity_number AS organisation_id,
        c.registered_charity_number AS charity_number,
        c.charity_name AS organisation_name,
        'Registered Charity' AS organisation_type,
        c.charity_company_registration_number AS company_number,
        n_charity.also_known_as,
        c.charity_contact_postcode AS postcode,
        CASE WHEN c.charity_contact_web ILIKE 'http:%%' THEN '' ELSE 'https://' END || c.charity_contact_web AS website,
        latest_income,
        latest_expenditure,
        pb.count_employees AS latest_employees,
        pa.count_volunteers AS latest_volunteers,
        t.latest_trustees,
        c.charity_registration_status AS registration_status,
        c.charity_reporting_status AS reporting_status,
        c.date_of_registration,
        c.date_of_removal,
        c.date_of_extract,
        c.charity_activities,
        c.charity_has_land,
        c.charity_is_cio
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
    SELECT o.org_id AS organisation_id,
        NULL AS charity_number,
        o.name AS organisation_name,
        CASE WHEN o."organisationTypePrimary_id" = 'community-interest-company' THEN 'Community Interest Company'
            WHEN o."organisationTypePrimary_id" = 'community-amateur-sports-club' THEN 'Community Amateur Sports Club'
            WHEN o."organisationTypePrimary_id" = 'community-benefit-society' THEN 'Mutual: Community Benefit Society'
            WHEN o."organisationTypePrimary_id" = 'working-mens-club' THEN 'Mutual: Working Mens Club'
            WHEN o."organisationTypePrimary_id" = 'registered-society' THEN 'Mutual: Registered Society'
            WHEN o."organisationTypePrimary_id" = 'co-operative-society' THEN 'Mutual: Co-operative Society'
            WHEN 'gp-practice' = ANY(o."organisationType")  THEN 'GP Practice'
            ELSE o."organisationTypePrimary_id" END AS organisation_type,
        c."CompanyNumber" AS company_number,
        o."alternateName" AS also_known_as,
        o."postalCode" AS postcode,
        o."url" AS website,
        NULL AS latest_income,
        NULL AS latest_expenditure,
        NULL AS latest_employees,
        NULL AS latest_volunteers,
        NULL AS latest_trustees,
        c."CompanyStatus" AS registration_status,
        c."Accounts_AccountCategory" AS reporting_status,
        o."dateRegistered"  AS date_of_registration,
        o."dateRemoved" AS date_of_removal,
        o."dateModified"::date AS date_of_extract,
        NULL AS charity_activities,
        NULL AS charity_has_land,
        NULL AS charity_is_cio
    FROM ftc_organisation o
        LEFT OUTER JOIN companies_company c
            ON o.org_id = 'GB-COH-' || c."CompanyNumber"
    WHERE o."organisationTypePrimary_id" IN (
        'community-interest-company',
        'community-amateur-sports-club',
        'community-benefit-society',
        'working-mens-club',
        'registered-society',
        'co-operative-society'
    )
        OR 'gp-practice' = ANY("organisationType")
), l AS (
    SELECT l.org_id AS organisation_id,
        STRING_AGG(ward."geoCode", ',') FILTER (WHERE l."locationType" = 'HQ') AS ward_code,
        STRING_AGG(ward.name, ',') FILTER (WHERE l."locationType" = 'HQ') AS ward_name,
        STRING_AGG(la."geoCode", ',') FILTER (WHERE l."locationType" = 'HQ') AS la_code,
        STRING_AGG(la.name, ',') FILTER (WHERE l."locationType" = 'HQ') AS la_name,
        STRING_AGG(rgn."geoCode", ',') FILTER (WHERE l."locationType" = 'HQ') AS rgn_code,
        STRING_AGG(rgn.name, ',') FILTER (WHERE l."locationType" = 'HQ') AS rgn_name,
        STRING_AGG(uk_ctry."geoCode", ',') FILTER (WHERE l."locationType" = 'HQ') AS uk_ctry_code,
        STRING_AGG(uk_ctry.name, ',') FILTER (WHERE l."locationType" = 'HQ') AS uk_ctry_name,
        (COUNT(*) FILTER (WHERE rgn."geoCode" = 'E12000007' AND l."locationType" = 'HQ')) > 0 AS hq_london,
        (COUNT(*) FILTER (WHERE rgn."geoCode" = 'E12000007')) > 0 AS london,
        MAX(l.geo_lat) FILTER (WHERE l."locationType" = 'HQ') AS latitude,
        MAX(l.geo_long) FILTER (WHERE l."locationType" = 'HQ') AS longitude
    FROM ftc_organisationlocation l
        LEFT OUTER JOIN geo_geolookup la
            ON l.geo_laua = la."geoCode"
        LEFT OUTER JOIN geo_geolookup rgn
            ON l.geo_rgn= rgn."geoCode"
        LEFT OUTER JOIN geo_geolookup uk_ctry
            ON l.geo_ctry= uk_ctry."geoCode"
        LEFT OUTER JOIN geo_geolookup ward
            ON l.geo_ward= ward."geoCode"
    GROUP BY 1
    ORDER BY l.org_id
),
cqc AS (
    SELECT DISTINCT ON (org_id) 
        org_id,
        id AS cqc_id,
        sector,
        directorate,
        inspection_category
    FROM other_data_cqcprovider
    WHERE org_id IS NOT NULL
)
SELECT main.organisation_id,
    main.charity_number,
    main.organisation_name,
    main.organisation_type::text,
    main.company_number,
    main.also_known_as,
    main.postcode,
    main.website,
    main.latest_income,
    main.latest_expenditure,
    main.latest_employees,
    main.latest_volunteers,
    main.latest_trustees,
    main.registration_status,
    main.reporting_status,
    main.date_of_registration,
    main.date_of_removal,
    main.date_of_extract,
    l.la_code::varchar(200) AS hq_la_code,
    l.la_name::varchar(255) AS hq_la_name,
    l.rgn_code::varchar(200) AS hq_rgn_code,
    l.rgn_name::varchar(255) AS hq_rgn_name,
    l.uk_ctry_code::varchar(200) AS hq_ctry_code,
    l.uk_ctry_name::varchar(255) AS hq_ctry_name,
    l.hq_london AS hq_london,
    l.ward_code::varchar(200) AS hq_ward_code,
    l.ward_name::varchar(255) AS hq_ward_name,
    main.charity_activities,
    l.london AS any_london,
    cqc.inspection_category AS cqc_category,
    main.charity_has_land,
    main.charity_is_cio,
    l.latitude,
    l.longitude
FROM main 
    LEFT OUTER JOIN l 
        ON main.organisation_id = l.organisation_id
    LEFT OUTER JOIN cqc
        ON main.organisation_id = cqc.org_id
WHERE l.london
"""
