from django.core import management

from ftc.management.commands._base_scraper import SQLRunner

UPDATE_GEODATA_SQL = {
    "Remove personal data in Organisations": """
        UPDATE ftc_organisation
        SET "streetAddress" = NULL,
            "addressLocality" = NULL,
            "addressRegion" = NULL,
            "addressCountry" = NULL,
            "postalCode" = NULL,
            "telephone" = NULL,
            "email" = NULL,
            "url" = NULL
        FROM ftc_personaldata pd
        WHERE pd.org_id = ANY(ftc_organisation.linked_orgs)
    """,
    "Remove personal data in Companies": """
        UPDATE companies_company
        SET "RegAddress_CareOf" = NULL,
            "RegAddress_POBox" = NULL,
            "RegAddress_AddressLine1" = NULL,
            "RegAddress_AddressLine2" = NULL,
            "RegAddress_PostTown" = NULL,
            "RegAddress_County" = NULL,
            "RegAddress_Country" = NULL,
            "RegAddress_PostCode" = NULL
        FROM ftc_personaldata pd
        WHERE pd.org_id ILIKE 'GB-COH-%%'
            AND pd.org_id = CONCAT('GB-COH-', "CompanyNumber")
    """,
    "Remove personal data in Charities": """
        UPDATE charity_charity
        SET address = NULL,
            postcode = NULL,
            phone = NULL,
            web = NULL,
            email = NULL
        FROM ftc_personaldata pd
        WHERE (
                pd.org_id ILIKE 'GB-CHC-%%' OR 
                pd.org_id ILIKE 'GB-NIC-%%' OR 
                pd.org_id ILIKE 'GB-SC-%%'
            )
            AND pd.org_id = id;
    """,
    "Remove personal data in Organisation Location": """
        DELETE
        FROM ftc_organisationlocation 
        WHERE org_id IN (
            SELECT o.org_id
            FROM ftc_organisation o
                INNER JOIN ftc_personaldata pd
                    ON pd.org_id = ANY(o.linked_orgs)
)
    """,
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
            "org_id",
            "name",
            "description",
            "geoCode",
            "geoCodeType",
            "locationType",
            "geo_iso",
            "spider",
            "source_id",
            "scrape_id"
        )
        select fo.org_id,
            'England' as name,
            fo.description,
            'E92000001' as "geoCode",
            fo."geoCodeType",
            fo."locationType",
            fo.geo_iso,
            fo.spider,
            fo.source_id,
            fo.scrape_id
        from ftc_organisationlocation fo
        where fo."geoCode" = 'K04000001'
            and "geoCodeType" = 'ONS'
        union
        select fo.org_id,
            'Wales' as name,
            fo.description,
            'W92000004' as "geoCode",
            fo."geoCodeType",
            fo."locationType",
            fo.geo_iso,
            fo.spider,
            fo.source_id,
            fo.scrape_id
        from ftc_organisationlocation fo
        where fo."geoCode" = 'K04000001'
            and "geoCodeType" = 'ONS'
        on conflict (org_id, "name", "geoCodeType", "locationType", spider, source_id, scrape_id) do nothing;
    """,
    'remove any "ENGLAND AND WALES" references': """
        delete from ftc_organisationlocation fo
        where fo."geoCode" = 'K04000001'
            and "geoCodeType" = 'ONS';
    """,
    "add postcode data to location from organisation table": """
        insert into ftc_organisationlocation (
            org_id,
            name,
            "geoCode",
            "geoCodeType",
            "locationType",
            geo_iso,
            "geo_oa11",
            "geo_oa21",
            "geo_cty",
            "geo_ctry",
            "geo_laua",
            "geo_ward",
            "geo_rgn",
            "geo_pcon",
            "geo_ttwa",
            "geo_lsoa11",
            "geo_lsoa21",
            "geo_msoa11",
            "geo_msoa21",
            "geo_lep1",
            "geo_lep2",
            "geo_lat",
            "geo_long",
            "spider",
            "source_id",
            "scrape_id"
        )
        select fo.org_id as org_id,
            fo."postalCode" as name,
            geo.pcds as "geoCode",
            'PC' as "geoCodeType",
            'HQ' as "locationType",
            'GB' as geo_iso,
            geo.oa11 as "geo_oa11",
            geo.oa21 as "geo_oa21",
            geo.cty as "geo_cty",
            geo.ctry as "geo_ctry",
            geo.laua as "geo_laua",
            geo.ward as "geo_ward",
            geo.rgn as "geo_rgn",
            geo.pcon as "geo_pcon",
            geo.ttwa as "geo_ttwa",
            geo.lsoa11 as "geo_lsoa11",
            geo.lsoa21 as "geo_lsoa21",
            geo.msoa11 as "geo_msoa11",
            geo.msoa21 as "geo_msoa21",
            geo.lep1 as "geo_lep1",
            geo.lep2 as "geo_lep2",
            geo.lat as "geo_lat",
            geo.long as "geo_long",
            fo.spider as spider,
            fo.source_id as source_id,
            fo.scrape_id as scrape_id
        from ftc_organisation fo
            inner join geo_postcode geo
                on fo."postalCode" = geo.pcds
        on conflict (org_id, "name", "geoCodeType", "locationType", spider, source_id, scrape_id) do nothing;
    """,
    "delete any records from location that aren't based on current scrapes": """
        delete from ftc_organisationlocation fo
        where fo.scrape_id not in (
            select ftc_scrape.id
            from ftc_scrape
            inner join (
                select spider,
                    max(finish_time) as latest_scrape
                from ftc_scrape
                where status = 'success'
                group by spider
            ) as latest_scrapes on ftc_scrape.spider = latest_scrapes.spider
                and ftc_scrape.finish_time = latest_scrapes.latest_scrape
        )
    """,
    "add missing area information for postcodes": """
        update ftc_organisationlocation
        set geo_iso = 'GB',
            geo_oa11 = geo.oa11,
            geo_oa21 = geo.oa21,
            geo_cty = geo.cty,
            geo_ctry = geo.ctry,
            geo_laua = geo.laua,
            geo_ward = geo.ward,
            geo_rgn = geo.rgn,
            geo_pcon = geo.pcon,
            geo_ttwa = geo.ttwa,
            geo_lsoa11 = geo.lsoa11,
            geo_lsoa21 = geo.lsoa21,
            geo_msoa11 = geo.msoa11,
            geo_msoa21 = geo.msoa21,
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
            geo_oa21 = geo.geo_oa21,
            geo_cty = geo.geo_cty,
            geo_ctry = geo.geo_ctry,
            geo_laua = geo.geo_laua,
            geo_ward = geo.geo_ward,
            geo_rgn = geo.geo_rgn,
            geo_pcon = geo.geo_pcon,
            geo_ttwa = geo.geo_ttwa,
            geo_lsoa11 = geo.geo_lsoa11,
            geo_lsoa21 = geo.geo_lsoa21,
            geo_msoa11 = geo.geo_msoa11,
            geo_msoa21 = geo.geo_msoa21,
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


class Command(SQLRunner):
    help = "Update geodata on organisations"
    name = "update_geodata"
    models_to_delete = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_sql = UPDATE_GEODATA_SQL

    def run_scraper(self, *args, **options):
        try:
            management.call_command("import_geolookups")
        except Exception:
            self.stdout.write(self.style.ERROR("Command import_geolookups failed"))
        # close the spider
        self.close_spider()
        self.logger.info("Spider finished")
