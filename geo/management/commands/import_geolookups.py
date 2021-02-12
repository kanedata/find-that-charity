import io
import csv
from collections import namedtuple

from ftc.management.commands._base_scraper import BaseScraper
from geo.models import GeoLookup

GeoSource = namedtuple('GeoSource', ['link', "type", 'codefield', 'namefield'])


class Command(BaseScraper):

    name = "geo_lookups"
    bulk_limit = 50000
    GEO_SOURCES = {
        "la": GeoSource("https://github.com/drkane/geo-lookups/raw/master/la_all_codes.csv", "la", "LADCD", "LADNM"),
        "utla": GeoSource("https://github.com/drkane/geo-lookups/raw/master/utla_all_codes.csv", "utla", "UTLACD", "UTLANM"),
        "lsoa": GeoSource("https://github.com/drkane/geo-lookups/raw/master/lsoa_la.csv", "lsoa", "LSOA11CD", "LSOA11NM"),
        "msoa": GeoSource("https://github.com/drkane/geo-lookups/raw/master/msoa_la.csv", "msoa", "MSOA11CD", "MSOA11HCLNM"),
        "ward": GeoSource("https://github.com/drkane/geo-lookups/raw/master/ward_all_codes.csv", "ward", "WDCD", "WDNM"),
    }

    FIELD_MATCH = {
        "WDCD": "geo_ward",  # ward code (may be out of date)
        "LSOA11CD": "geo_lsoa11",  # Lower Super Output Area code
        "MSOA11CD": "geo_msoa11",  # Middle Super Output Area code
        "LAD20CD": "geo_laua",  # Local Authority (2020) code
        "UTLACD": "geo_cty",  # Upper tier local authority code
        # "CAUTHCD": "geo_",  # Combined authority code
        "RGNCD": "geo_rgn",  # Region code
        "CTRYCD": "geo_ctry",  # Country code
        "TTWA11CD": "geo_ttwa",  # Travel to work area code
    }

    MANUAL_RECORDS = (
        {"geoCode": "E92000001", "geoCodeType": "ctry", "geo_iso": "GB", "geo_ctry": "E92000001", "name": "England"},
        {"geoCode": "S92000003", "geoCodeType": "ctry", "geo_iso": "GB", "geo_ctry": "S92000003", "name": "Scotland"},
        {"geoCode": "N92000002", "geoCodeType": "ctry", "geo_iso": "GB", "geo_ctry": "N92000002", "name": "Northern Ireland"},
        {"geoCode": "W92000004", "geoCodeType": "ctry", "geo_iso": "GB", "geo_ctry": "W92000004", "name": "Wales"},
        {"geoCode": "E12000001", "geoCodeType": "rgn", "geo_iso": "GB", "geo_ctry": "E92000001", "geo_rgn": "E12000001", "name": "North East"},
        {"geoCode": "E12000002", "geoCodeType": "rgn", "geo_iso": "GB", "geo_ctry": "E92000001", "geo_rgn": "E12000002", "name": "North West"},
        {"geoCode": "E12000003", "geoCodeType": "rgn", "geo_iso": "GB", "geo_ctry": "E92000001", "geo_rgn": "E12000003", "name": "Yorkshire and The Humber"},
        {"geoCode": "E12000004", "geoCodeType": "rgn", "geo_iso": "GB", "geo_ctry": "E92000001", "geo_rgn": "E12000004", "name": "East Midlands"},
        {"geoCode": "E12000005", "geoCodeType": "rgn", "geo_iso": "GB", "geo_ctry": "E92000001", "geo_rgn": "E12000005", "name": "West Midlands"},
        {"geoCode": "E12000006", "geoCodeType": "rgn", "geo_iso": "GB", "geo_ctry": "E92000001", "geo_rgn": "E12000006", "name": "East of England"},
        {"geoCode": "E12000007", "geoCodeType": "rgn", "geo_iso": "GB", "geo_ctry": "E92000001", "geo_rgn": "E12000007", "name": "London"},
        {"geoCode": "E12000008", "geoCodeType": "rgn", "geo_iso": "GB", "geo_ctry": "E92000001", "geo_rgn": "E12000008", "name": "South East"},
        {"geoCode": "E12000009", "geoCodeType": "rgn", "geo_iso": "GB", "geo_ctry": "E92000001", "geo_rgn": "E12000009", "name": "South West"},
    )

    def run_scraper(self, *args, **options):

        # initialise records
        self.files = {}
        self.records = {}
        self.object_count = 0

        # delete existing records
        GeoLookup.objects.all().delete()
        self.logger.info("Deleting existing items")

        # create the manual records
        for m in self.MANUAL_RECORDS:
            self.add_record(**m)

        # download the files
        for k, source in self.GEO_SOURCES.items():
            if source.link.startswith("http"):
                self.set_session(False)
                self.logger.info("Downloading from {}".format(source.link))
                response = self.session.get(source.link)
                response.raise_for_status()
                self.files[k] = io.BytesIO(response.content)
            else:
                self.logger.info("Opening {}".format(source.link))
                self.files[k] = open(source.link, "rb")

        # go through each geolookup file and create records
        for k, f in self.files.items():
            reader = csv.DictReader(
                io.TextIOWrapper(f, encoding="utf-8-sig")
            )
            self.logger.info("Opening file {}".format(k))
            for row in reader:
                self.parse_row(row, self.GEO_SOURCES[k])

        self.close_spider()

    def parse_row(self, row, geocodetype):

        for k, v in row.items():
            if not v or v == "":
                row[k] = None

        self.add_record(
            geoCode=row[geocodetype.codefield],
            geoCodeType=geocodetype.type,
            geo_iso="GB",
            name=row[geocodetype.namefield],
            **{
                v: row[k]
                for k, v in self.FIELD_MATCH.items()
                if row.get(k)
            }
        )

    def add_record(self, **kwargs):
        self.records[kwargs["geoCode"]] = GeoLookup(**kwargs)

    def commit_records(self):
        self.object_count += len(self.records)
        self.logger.info("Saving {:,.0f} records".format(len(self.records)))
        GeoLookup.objects.bulk_create(self.records.values())
        self.logger.info(
            "Saved {:,.0f} records ({:,.0f} total)".format(
                len(self.records),
                self.object_count,
            )
        )

    def close_spider(self):
        self.commit_records()
        self.scrape.items = self.object_count
        results = {"records": self.object_count}
        self.scrape.errors = self.error_count
        self.scrape.result = results
        self.scrape_logger.teardown()
