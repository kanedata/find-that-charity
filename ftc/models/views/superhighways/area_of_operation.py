from django.db import models
from django_db_views.db_view import DBView


class SuperhighwaysAreaOfOperation(DBView):
    organisation_id = models.CharField(max_length=255)
    charity_number = models.IntegerField(null=True)
    company_number = models.IntegerField(null=True)
    location_type = models.CharField(max_length=255, null=True)
    la_code = models.CharField(max_length=200, null=True)
    la_name = models.CharField(max_length=255, null=True)
    rgn_code = models.CharField(max_length=200, null=True)
    rgn_name = models.CharField(max_length=255, null=True)
    uk_ctry_code = models.CharField(max_length=200, null=True)
    uk_ctry_name = models.CharField(max_length=255, null=True)
    ctry_code = models.CharField(max_length=200, null=True)
    ctry_name = models.CharField(max_length=255, null=True)
    london = models.BooleanField(null=True)
    ward_code = models.CharField(max_length=200, null=True)
    ward_name = models.CharField(max_length=255, null=True)

    class Meta:
        managed = False
        db_table = "superhighways_area_of_operation"

    view_definition = """
SELECT l.org_id AS organisation_id,
        CASE
            WHEN l.org_id::text ~~* 'GB-CHC-%%'::text THEN replace(l.org_id::text, 'GB-CHC-'::text, ''::text)::integer
            ELSE NULL::integer
        END AS charity_number,
        CASE
            WHEN l.org_id::text ~~* 'GB-COH-%%'::text THEN replace(l.org_id::text, 'GB-COH-'::text, ''::text)
            ELSE NULL::text
        END AS company_number,
    l."locationType" AS location_type,
    la."geoCode" AS la_code,
    la.name AS la_name,
    rgn."geoCode" AS rgn_code,
    rgn.name AS rgn_name,
    uk_ctry."geoCode" AS uk_ctry_code,
    uk_ctry.name AS uk_ctry_name,
    ctry."geoCode" AS ctry_code,
    ctry.name AS ctry_name,
    rgn."geoCode" IS NOT NULL AND rgn."geoCode"::text = 'E12000007'::text AS london,
    ward."geoCode" AS ward_code,
    ward.name AS ward_name
FROM ftc_organisationlocation l
    LEFT JOIN geo_geolookup la ON l.geo_laua::text = la."geoCode"::text
    LEFT JOIN geo_geolookup rgn ON l.geo_rgn::text = rgn."geoCode"::text
    LEFT JOIN geo_geolookup uk_ctry ON l.geo_ctry::text = uk_ctry."geoCode"::text
    LEFT JOIN geo_geolookup ctry ON l.geo_iso::text = ctry."geoCode"::text
    LEFT JOIN geo_geolookup ward ON l.geo_ward::text = ward."geoCode"::text
    INNER JOIN superhighways_london_organisations so ON so.organisation_id = l.org_id  
ORDER BY l.org_id
"""
