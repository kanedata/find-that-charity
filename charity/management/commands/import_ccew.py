# -*- coding: utf-8 -*-
import os
import re
import tempfile
import zipfile

import bcp
import psycopg2
import tqdm
from django.db import connection
from django.core.management.base import CommandError

from charity.feeds import CCEW_DATA_URL
from charity.management.commands._ccew_sql import UPDATE_CCEW
from charity.models import (CCEWCharity, CCEWCharityAOO, CCEWClass,
                            CCEWFinancial, CCEWMainCharity, CCEWName,
                            CCEWObjects, CCEWPartB, CCEWRegistration)
from ftc.management.commands._base_scraper import HTMLScraper
from ftc.models import Organisation, OrganisationLink, Scrape


class Command(HTMLScraper):
    name = "ccew"
    custom_settings = {
        "DOWNLOAD_TIMEOUT": 180 * 3,
        "REDIS_URL": os.environ.get("REDIS_URL"),
    }
    allowed_domains = ["charitycommission.gov.uk"]
    start_urls = [
        CCEW_DATA_URL,
        # "https://raw.githubusercontent.com/drkane/charity-lookups/master/cc-aoo-gss-iso.csv",
    ]
    org_id_prefix = "GB-CHC"
    id_field = "regno"
    date_fields = []
    date_format = "%Y-%m-%d %H:%M:%S"
    zip_regex = re.compile(
        r".*/RegPlusExtract.*?\.zip.*?"
    )
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
                "accessURL": "",
                "title": "Registered charities in England and Wales",
            }
        ],
    }
    ccew_file_to_object = {
        "extract_charity": CCEWCharity,
        "extract_main_charity": CCEWMainCharity,
        "extract_name": CCEWName,
        "extract_registration": CCEWRegistration,
        "extract_charity_aoo": CCEWCharityAOO,
        "extract_objects": CCEWObjects,
        "extract_financial": CCEWFinancial,
        "extract_class": CCEWClass,
        "extract_partb": CCEWPartB,
    }
    ccew_files = {
        "extract_charity": [
            "regno",  # integer      registered number of a charity
            "subno",  # integer      subsidiary number of a charity (may be 0 for main/group charity)
            "name",  # varchar(150)  main name of the charity
            "orgtype",  # varchar(2)  R (registered) or RM (removed)
            "gd",  # varchar(250)  Description of Governing Document
            "aob",  # varchar(175)  area of benefit - may not be defined
            "aob_defined",  # char(1)      area of benefit defined by Governing Document (T/F)
            "nhs",  # char(1)      NHS charity (T/F)
            "ha_no",  # varchar(20)  Housing Association number
            "corr",  # varchar(70)  Charity correspondent name
            "add1",  # varchar(35)  address line of charity's correspondent
            "add2",  # varchar(35)  address line of charity's correspondent
            "add3",  # varchar(35)  address line of charity's correspondent
            "add4",  # varchar(35)  address line of charity's correspondent
            "add5",  # varchar(35)  address line of charity's correspondent
            "postcode",  # varchar(8)  postcode of charity's correspondent
            "phone",  # varchar(23)  telephone of charity's correspondent
            "fax",  # varchar(23)  fax of charity's correspondent
        ],
        "extract_main_charity": [
            "regno",  # integer      registered number of a charity
            "coyno",  # integer      company registration number
            "trustees",  # char(1)      trustees incorporated (T/F)
            "fyend",  # char(4)      Financial year end
            "welsh",  # char(1)      requires correspondence in both Welsh & English (T/F)
            "incomedate",  # datetime      date for latest gross income (blank if income is an estimate)
            "income",  # integer
            "grouptype",  # varchar(4)      may be blank
            "email",  # varchar(255)  email address
            "web",  # varchar(255)  website address
        ],
        "extract_name": [
            "regno",  # integer      registered number of a charity
            "subno",  # integer      subsidiary number of a charity (may be 0 for main/group charity)
            "nameno",  # integer      number identifying a charity name
            "name",  # varchar(150)  name of a charity (multiple occurrences possible)
        ],
        "extract_registration": [
            "regno",  # integer      registered number of a charity
            "subno",  # integer      subsidiary number of a charity (may be 0 for main/group charity)
            "regdate",  # datetime      date of registration for a charity
            "remdate",  # datetime      Removal date of a charity - Blank for Registered Charities
            "remcode",  # varchar(3)      Register removal reason code
        ],
        "extract_charity_aoo": [
            "regno",  # integer      registered number of a charity
            "aootype",  # char(1)      A B or D
            "aookey",  # integer      up to three digits
            "welsh",  # char(1)      Flag: Y or blank
            "master",  # integer      may be blank. If aootype=D then holds continent; if aootype=B then holds GLA/met county
        ],
        "extract_objects": [
            "regno",  # integer      registered number of a charity
            "subno",  # integer      subsidiary number of a charity (may be 0 for main/group charity)
            "seqno",  # char(4)      sequence number (in practice 0-20)
            "object",  # varchar(255)  Description of objects of a charity
        ],
        "extract_financial": [
            "regno",  # integer  registered number of a charity
            "fystart",  # datetime  Charity's financial year start date
            "fyend",  # datetime  Charity's financial year end date
            "income",  # integer
            "expend",  # integer
        ],
        "extract_class": [
            "regno",  # integer  registered number of a charity
            "class",  # integer  classification code for a charity(multiple occurrences possible)
        ],
        "extract_partb": [
            "regno",
            "artype",
            "fystart",
            "fyend",
            "inc_leg",
            "inc_end",
            "inc_vol",
            "inc_fr",
            "inc_char",
            "inc_invest",
            "inc_other",
            "inc_total",
            "invest_gain",
            "asset_gain",
            "pension_gain",
            "exp_vol",
            "exp_trade",
            "exp_invest",
            "exp_grant",
            "exp_charble",
            "exp_gov",
            "exp_other",
            "exp_total",
            "exp_support",
            "exp_dep",
            "reserves",
            "asset_open",
            "asset_close",
            "fixed_assets",
            "open_assets",
            "invest_assets",
            "cash_assets",
            "current_assets",
            "credit_1",
            "credit_long",
            "pension_assets",
            "total_assets",
            "funds_end",
            "funds_restrict",
            "funds_unrestrict",
            "funds_total",
            "employees",
            "volunteers",
            "cons_acc",
            "charity_acc",
        ],
    }
    orgtypes = [
        "Registered Charity",
        "Registered Charity (England and Wales)",
        "Registered Company",
        "Incorporated Charity",
        "Charitable Incorporated Organisation",
        "Charitable Incorporated Organisation - Association",
        "Charitable Incorporated Organisation - Foundation",
    ]

    def parse_file(self, response, source_urls):
        zip_found = False
        for link in response.html.absolute_links:
            if ".zip" not in link or "TableBuildScripts" in link:
                continue
            self.set_download_url(link)
            self.logger.info("Using file: {}".format(link))
            zip_found = True
            r = self.session.get(link)
            r.raise_for_status()
            self.process_zip(r)
            break

        if not zip_found:
            raise CommandError("No zip file found")

    def process_zip(self, response):
        self.logger.info("File size: {}".format(len(response.content)))

        with tempfile.TemporaryDirectory() as tmpdirname:
            cczip_name = os.path.join(tmpdirname, "ccew.zip")
            files = {}

            with open(cczip_name, "wb") as cczip:
                self.logger.info("Saving ZIP to disk")
                cczip.write(response.content)

            with zipfile.ZipFile(cczip_name, "r") as z:
                for f in z.infolist():
                    filename = f.filename.replace(".bcp", "")
                    filepath = os.path.join(tmpdirname, f.filename)
                    if filename not in self.ccew_files.keys():
                        self.logger.debug("Skipping: {}".format(f.filename))
                        continue
                    self.logger.info("Saving {} to disk".format(f.filename))
                    z.extract(f, path=tmpdirname)
                    files[filename] = filepath

            for filename, filepath in files.items():
                with open(filepath, "r", encoding="latin1") as bcpfile:
                    self.logger.info("Processing: {}".format(filename))
                    self.process_bcp(bcpfile, filename)

    def process_bcp(self, bcpfile, filename):

        fields = self.ccew_files.get(filename)
        db_table = self.ccew_file_to_object.get(filename)
        page_size = 1000
        self.date_fields = [f for f in fields if f.endswith("date")]

        def get_data(bcpreader):
            for k, row in tqdm.tqdm(enumerate(bcpreader)):
                row = self.clean_fields(row)
                if not row.get("regno"):
                    continue
                yield [k] + list(row.values())

        with connection.cursor() as cursor:
            bcpreader = bcp.DictReader(bcpfile, fieldnames=fields)
            self.logger.info(
                "Starting table insert [{}]".format(db_table._meta.db_table)
            )
            db_table.objects.all().delete()
            psycopg2.extras.execute_values(
                cursor,
                """INSERT INTO {} VALUES %s;""".format(db_table._meta.db_table),
                get_data(bcpreader),
                page_size=page_size,
            )
            self.logger.info(
                "Finished table insert [{}]".format(db_table._meta.db_table)
            )

    def close_spider(self):

        # execute SQL statements
        with connection.cursor() as cursor:
            for sql_name, sql in UPDATE_CCEW.items():
                self.logger.info("Starting SQL: {}".format(sql_name))
                cursor.execute(sql.format(scrape_id=self.scrape.id, source=self.name,))
                self.logger.info("Finished SQL: {}".format(sql_name))

        self.object_count = Organisation.objects.filter(
            spider__exact=self.name, scrape_id=self.scrape.id,
        ).count()
        self.scrape.items = self.object_count
        results = {"records": self.object_count}
        self.logger.info("Saved {:,.0f} organisation records".format(self.object_count))

        link_records_count = OrganisationLink.objects.filter(
            spider__exact=self.name, scrape_id=self.scrape.id,
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
            Organisation.objects.filter(spider__exact=self.name,).exclude(
                scrape_id=self.scrape.id,
            ).delete()
            OrganisationLink.objects.filter(spider__exact=self.name,).exclude(
                scrape_id=self.scrape.id,
            ).delete()
            self.logger.info("Deleted previous records")
