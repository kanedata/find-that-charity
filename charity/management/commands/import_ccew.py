# -*- coding: utf-8 -*-
import csv
import io
import re
import zipfile

import psycopg2
import tqdm

from charity.management.commands._ccew_sql import UPDATE_CCEW
from charity.models import (
    CCEWCharity,
    CCEWCharityAnnualReturnHistory,
    CCEWCharityAreaOfOperation,
    CCEWCharityARPartA,
    CCEWCharityARPartB,
    CCEWCharityClassification,
    CCEWCharityEventHistory,
    CCEWCharityGoverningDocument,
    CCEWCharityOtherNames,
    CCEWCharityOtherRegulators,
    CCEWCharityPolicy,
    CCEWCharityPublishedReport,
    CCEWCharityTrustee,
)
from ftc.management.commands._base_scraper import BaseScraper
from ftc.models import (
    Organisation,
    OrganisationClassification,
    OrganisationLink,
    Scrape,
)


class Command(BaseScraper):
    name = "ccew"
    allowed_domains = ["charitycommission.gov.uk"]
    start_urls = []
    encoding = "utf8"
    org_id_prefix = "GB-CHC"
    id_field = "regno"
    date_fields = []
    date_format = "%Y-%m-%d %H:%M:%S"
    zip_regex = re.compile(r".*/RegPlusExtract.*?\.zip.*?")
    base_url = "https://ccewuksprdoneregsadata1.blob.core.windows.net/data/txt/publicextract.{}.zip"
    source = {
        "title": "Registered charities in England and Wales",
        "description": "Data download service provided by the Charity Commission",
        "identifier": "ccew",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/",
        "license_name": "Open Government Licence v2.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Charity Commission for England and Wales",
            "website": "https://www.gov.uk/charity-commission",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "https://register-of-charities.charitycommission.gov.uk/register/full-register-download",
                "title": "Registered charities in England and Wales",
            }
        ],
    }
    ccew_file_to_object = {
        "charity": CCEWCharity,
        "charity_annual_return_history": CCEWCharityAnnualReturnHistory,
        "charity_annual_return_parta": CCEWCharityARPartA,
        "charity_annual_return_partb": CCEWCharityARPartB,
        "charity_area_of_operation": CCEWCharityAreaOfOperation,
        "charity_classification": CCEWCharityClassification,
        "charity_event_history": CCEWCharityEventHistory,
        "charity_governing_document": CCEWCharityGoverningDocument,
        "charity_other_names": CCEWCharityOtherNames,
        "charity_other_regulators": CCEWCharityOtherRegulators,
        "charity_policy": CCEWCharityPolicy,
        "charity_published_report": CCEWCharityPublishedReport,
        "charity_trustee": CCEWCharityTrustee,
    }
    orgtypes = [
        "Registered Charity",
        "Registered Charity (England and Wales)",
        "Registered Company",
        "Incorporated Charity",
        "Charitable Incorporated Organisation",
        "Charitable Incorporated Organisation - Association",
        "Charitable Incorporated Organisation - Foundation",
        "Trust",
    ]

    def fetch_file(self):
        self.files = {}
        for filename in self.ccew_file_to_object:
            url = self.base_url.format(filename)
            self.set_download_url(url)
            r = self.session.get(url)
            r.raise_for_status()
            self.files[filename] = r

    def parse_file(self, response, filename):
        try:
            z = zipfile.ZipFile(io.BytesIO(response.content))
        except zipfile.BadZipFile:
            self.logger.info(response.content[0:1000])
            raise
        for f in z.infolist():
            self.logger.info("Opening: {}".format(f.filename))
            with z.open(f) as csvfile:
                self.process_file(csvfile, filename)
        z.close()

    def process_file(self, csvfile, filename):
        db_table = self.ccew_file_to_object.get(filename)
        page_size = 1000

        def get_data(reader, row_count=None):
            for k, row in tqdm.tqdm(enumerate(reader)):
                row = self.clean_fields(row)
                if row_count and row_count != (len(row) + 1):
                    self.logger.info(row)
                    raise ValueError(
                        "Incorrect number of rows (expected {} and got {})".format(
                            row_count,
                            len(row) + 1,
                        )
                    )
                yield [k] + list(row.values())

        reader = csv.DictReader(
            io.TextIOWrapper(csvfile, encoding=self.encoding),
            delimiter="\t",
            escapechar="\\",
            quoting=csv.QUOTE_NONE,
        )
        self.logger.info("Starting table insert [{}]".format(db_table._meta.db_table))
        db_table.objects.all().delete()
        statement = """INSERT INTO "{table}" ("{fields}") VALUES %s;""".format(
            table=db_table._meta.db_table,
            fields='", "'.join(["id"] + list(reader.fieldnames)),
        )
        psycopg2.extras.execute_values(
            self.cursor,
            statement,
            get_data(reader, len(reader.fieldnames) + 1),
            page_size=page_size,
        )
        self.logger.info("Finished table insert [{}]".format(db_table._meta.db_table))

    def close_spider(self):
        # execute SQL statements
        self.execute_sql_statements(UPDATE_CCEW)

        self.object_count = Organisation.objects.filter(
            spider__exact=self.name,
            scrape_id=self.scrape.id,
        ).count()
        self.scrape.items = self.object_count
        results = {"records": self.object_count}
        self.logger.info("Saved {:,.0f} organisation records".format(self.object_count))

        link_records_count = OrganisationLink.objects.filter(
            spider__exact=self.name,
            scrape_id=self.scrape.id,
        ).count()
        if link_records_count:
            results["link_records"] = link_records_count
            self.object_count += results["link_records"]
            self.logger.info(
                "Saved {:,.0f} link records".format(results["link_records"])
            )

        self.scrape.errors = self.error_count
        self.scrape.result = results
        if self.object_count == 0:
            self.scrape.status = Scrape.ScrapeStatus.FAILED
        elif self.error_count > 0:
            self.scrape.status = Scrape.ScrapeStatus.ERRORS
        else:
            self.scrape.status = Scrape.ScrapeStatus.SUCCESS
        self.scrape.save()

        # if we've been successfull then delete previous items
        if self.object_count > 0:
            self.logger.info("Deleting previous records")
            Organisation.objects.filter(
                spider__exact=self.name,
            ).exclude(
                scrape_id=self.scrape.id,
            ).delete()
            OrganisationLink.objects.filter(
                spider__exact=self.name,
            ).exclude(
                scrape_id=self.scrape.id,
            ).delete()
            OrganisationClassification.objects.filter(
                spider__exact=self.name,
            ).exclude(
                scrape_id=self.scrape.id,
            ).delete()
            self.logger.info("Deleted previous records")
