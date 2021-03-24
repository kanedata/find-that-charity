import logging

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):

    update_sql = {
        "Remove blank postcodes": """
            update ftc_organisation
            set "postalCode" = null
            where trim("postalCode") = '';
        """,
        "Update misformatted postcodes": """
            update ftc_organisation
            set "postalCode" = concat_ws(
                ' ',
                trim(left(replace("postalCode", ' ', ''), length(replace("postalCode", ' ', ''))-3)),
                right(replace("postalCode", ' ', ''), 3)
            )
            where "postalCode" is not null;
        """,
        'convert "ENGLAND AND WALES" to "ENGLAND" and "WALES"': """
            insert into ftc_organisationlocation (
                "organisation_id",
                "org_id",
                "name",
                "description",
                "geoCode",
                "geoCodeType",
                "locationType",
                "geo_iso",
                "source_id",
                "scrape_id"
            )
            select fo.organisation_id,
                fo.org_id,
                'England' as name,
                fo.description,
                'E92000001' as "geoCode",
                fo."geoCodeType",
                fo."locationType",
                fo.geo_iso,
                fo.source_id,
                fo.scrape_id
            from ftc_organisationlocation fo
            where fo."geoCode" = 'K04000001'
                and "geoCodeType" = 'ONS'
            union
            select fo.organisation_id,
                fo.org_id,
                'Wales' as name,
                fo.description,
                'W92000004' as "geoCode",
                fo."geoCodeType",
                fo."locationType",
                fo.geo_iso,
                fo.source_id,
                fo.scrape_id
            from ftc_organisationlocation fo
            where fo."geoCode" = 'K04000001'
                and "geoCodeType" = 'ONS';
        """,
        'remove any "ENGLAND AND WALES" references': """
            delete from ftc_organisationlocation fo
            where fo."geoCode" = 'K04000001'
                and "geoCodeType" = 'ONS';
        """,
        "add postcode data to location from organisation table": """
            insert into ftc_organisationlocation (
                organisation_id,
                org_id,
                name,
                "geoCode",
                "geoCodeType",
                "locationType",
                geo_iso,
                "geo_oa11",
                "geo_cty",
                "geo_ctry",
                "geo_laua",
                "geo_ward",
                "geo_rgn",
                "geo_pcon",
                "geo_ttwa",
                "geo_lsoa11",
                "geo_msoa11",
                "geo_lep1",
                "geo_lep2",
                "geo_lat",
                "geo_long",
                "source_id",
                "scrape_id"
            )
            select fo.id as organisation_id,
                fo.org_id as org_id,
                fo."postalCode" as name,
                geo.pcds as "geoCode",
                'PC' as "geoCodeType",
                'HQ' as "locationType",
                'GB' as geo_iso,
                geo.oa11 as "geo_oa11",
                geo.cty as "geo_cty",
                geo.ctry as "geo_ctry",
                geo.laua as "geo_laua",
                geo.ward as "geo_ward",
                geo.rgn as "geo_rgn",
                geo.pcon as "geo_pcon",
                geo.ttwa as "geo_ttwa",
                geo.lsoa11 as "geo_lsoa11",
                geo.msoa11 as "geo_msoa11",
                geo.lep1 as "geo_lep1",
                geo.lep2 as "geo_lep2",
                geo.lat as "geo_lat",
                geo.long as "geo_long",
                fo.source_id as source_id,
                fo.scrape_id as scrape_id
            from ftc_organisation fo
                inner join geo_postcode geo
                    on fo."postalCode" = geo.pcds;
        """,
        "delete any records from location that aren't based on current scrapes": """
            delete from ftc_organisationlocation
            where id in (
                select fol.id
                from ftc_organisationlocation fol
                    left outer join ftc_organisation fo
                        on fol.organisation_id = fo.id
                            and fol.scrape_id = fo.scrape_id
                where fo.scrape_id is null
            )
        """,
        "add missing area information for postcodes": """
            update ftc_organisationlocation
            set geo_iso = 'GB',
                geo_oa11 = geo.oa11,
                geo_cty = geo.cty,
                geo_ctry = geo.ctry,
                geo_laua = geo.laua,
                geo_ward = geo.ward,
                geo_rgn = geo.rgn,
                geo_pcon = geo.pcon,
                geo_ttwa = geo.ttwa,
                geo_lsoa11 = geo.lsoa11,
                geo_msoa11 = geo.msoa11,
                geo_lep1 = geo.lep1,
                geo_lep2 = geo.lep2,
                geo_lat = geo.lat,
                geo_long = geo.long
            from geo_postcode geo
            where ftc_organisationlocation."geoCode" = geo.pcds
                and ftc_organisationlocation."geoCodeType" = 'PC'
                and ftc_organisationlocation.geo_oa11 is null;
        """,
        "add missing area information for lookups": """
            update ftc_organisationlocation
            set geo_iso = 'GB',
                geo_oa11 = geo.geo_oa11,
                geo_cty = geo.geo_cty,
                geo_ctry = geo.geo_ctry,
                geo_laua = geo.geo_laua,
                geo_ward = geo.geo_ward,
                geo_rgn = geo.geo_rgn,
                geo_pcon = geo.geo_pcon,
                geo_ttwa = geo.geo_ttwa,
                geo_lsoa11 = geo.geo_lsoa11,
                geo_msoa11 = geo.geo_msoa11,
                geo_lep1 = geo.geo_lep1,
                geo_lep2 = geo.geo_lep2,
                geo_lat = geo.geo_lat,
                geo_long = geo.geo_long
            from geo_geolookup geo
            where ftc_organisationlocation."geoCode" = geo."geoCode"
                and ftc_organisationlocation."geoCodeType" = 'ONS'
                and ftc_organisationlocation.geo_ctry is null;
        """,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            for name, sql in self.update_sql.items():
                self.logger.info("Starting SQL {}".format(name))
                cursor.execute(sql)
                self.logger.info("Finished SQL {}".format(name))
