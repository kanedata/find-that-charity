# -*- coding: utf-8 -*-
import csv
import datetime
import io
import os
import pickle
import re
import tempfile
import zipfile
from collections import defaultdict

import bcp
import tqdm
from django.db import connection
from django.utils.text import slugify

from charity.management.commands._bulk_upsert import bulk_upsert
from charity.management.commands._ccew_sql import UPDATE_CCEW
from charity.models import (AreaOfOperation, Charity, CharityFinancial,
                            CharityName, CharityRaw)
from ftc.management.commands._base_scraper import HTMLScraper
from ftc.models import Organisation


class Command(HTMLScraper):
    name = 'ccew'
    custom_settings = {
        'DOWNLOAD_TIMEOUT': 180 * 3,
        'REDIS_URL': os.environ.get('REDIS_URL'),
    }
    allowed_domains = ['charitycommission.gov.uk']
    start_urls = [
        "http://data.charitycommission.gov.uk/",
        "https://raw.githubusercontent.com/drkane/charity-lookups/master/cc-aoo-gss-iso.csv",
    ]
    org_id_prefix = "GB-CHC"
    id_field = "regno"
    date_fields = []
    date_format = "%Y-%m-%d %H:%M:%S"
    zip_regex = re.compile(r"http://apps.charitycommission.gov.uk/data/.*?/RegPlusExtract.*?\.zip")
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
                "title": "Registered charities in England and Wales"
            }
        ],
    }
    ccew_files = {
        'extract_charity': [
            "regno", #	     integer 	    registered number of a charity
            "subno", #	     integer 	    subsidiary number of a charity (may be 0 for main/group charity)
            "name", #	     varchar(150) 	main name of the charity
            "orgtype", #	 varchar(2) 	R (registered) or RM (removed)
            "gd", #	         varchar(250) 	Description of Governing Document
            "aob", #	     varchar(175) 	area of benefit - may not be defined
            "aob_defined", # char(1) 	    area of benefit defined by Governing Document (T/F)
            "nhs", #         char(1) 	    NHS charity (T/F)
            "ha_no", #	     varchar(20) 	Housing Association number
            "corr", #	     varchar(70) 	Charity correspondent name
            "add1", #	     varchar(35) 	address line of charity's correspondent
            "add2", #	     varchar(35) 	address line of charity's correspondent
            "add3", #	     varchar(35) 	address line of charity's correspondent
            "add4", #	     varchar(35) 	address line of charity's correspondent
            "add5", #	     varchar(35) 	address line of charity's correspondent
            "postcode", #	 varchar(8) 	postcode of charity's correspondent
            "phone", #	     varchar(23) 	telephone of charity's correspondent
            "fax", #	     varchar(23) 	fax of charity's correspondent
        ],
        'extract_main_charity': [
            "regno", # 	    integer 	    registered number of a charity
            "coyno", # 	    integer 	    company registration number
            "trustees", # 	char(1) 	    trustees incorporated (T/F)
            "fyend", # 	    char(4) 	    Financial year end
            "welsh", # 	    char(1) 	    requires correspondence in both Welsh & English (T/F)
            "incomedate", # datetime 	    date for latest gross income (blank if income is an estimate)
            "income", # 	integer
            "grouptype", # 	varchar(4) 	    may be blank
            "email", # 	    varchar(255) 	email address
            "web", # 	    varchar(255) 	website address
        ],
        'extract_name': [
            "regno",  # 	integer 	    registered number of a charity
            "subno",  # 	integer 	    subsidiary number of a charity (may be 0 for main/group charity)
            "nameno", #  	integer 	    number identifying a charity name
            "name",   #     varchar(150) 	name of a charity (multiple occurrences possible)
        ],
        'extract_registration': [
            "regno", #   	integer 	    registered number of a charity
            "subno", #   	integer 	    subsidiary number of a charity (may be 0 for main/group charity)
            "regdate", #    datetime 	    date of registration for a charity
            "remdate", #    datetime 	    Removal date of a charity - Blank for Registered Charities
            "remcode", #    varchar(3) 	    Register removal reason code
        ],
        'extract_charity_aoo': [
            "regno", # 	    integer 	    registered number of a charity
            "aootype", # 	char(1) 	    A B or D
            "aookey", # 	integer 	    up to three digits
            "welsh", # 	    char(1) 	    Flag: Y or blank
            "master", # 	integer 	    may be blank. If aootype=D then holds continent; if aootype=B then holds GLA/met county
        ],
        'extract_objects': [
            "regno",  # 	integer 	    registered number of a charity
            "subno",  # 	integer 	    subsidiary number of a charity (may be 0 for main/group charity)
            "seqno",  # 	char(4) 	    sequence number (in practice 0-20)
            "object", #  	varchar(255) 	Description of objects of a charity
        ],
        'extract_financial': [
            "regno", # 	integer 	registered number of a charity
            "fystart", # 	datetime 	Charity's financial year start date
            "fyend", # 	datetime 	Charity's financial year end date
            "income", # 	integer 	
            "expend", # 	integer
        ],
        "extract_class": [
            "regno", # integer 	registered number of a charity
            "class", # integer 	classification code for a charity(multiple occurrences possible)
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
        self.redis = False
        for l in response.html.absolute_links:
            if not self.zip_regex.match(l):
                continue
            r = self.session.get(l)
            self.logger.info("Using file: {}".format(l))
            self.process_zip(r)

    def process_zip(self, response):
        self.logger.info("File size: {}".format(len(response.content)))
        self.initialise_charities()
        
        with tempfile.TemporaryDirectory() as tmpdirname:
            cczip_name = os.path.join(tmpdirname, 'ccew.zip')
            files = {}

            with open(cczip_name, 'wb') as cczip:
                self.logger.info("Saving ZIP to disk")
                cczip.write(response.content)

            with zipfile.ZipFile(cczip_name, 'r') as z:
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
                with open(filepath, 'r', encoding='latin1') as bcpfile:
                    self.logger.info("Processing: {}".format(filename))
                    self.process_bcp(bcpfile, filename)

        return self.process_charities()

    def process_bcp(self, bcpfile, filename):

        fields = self.ccew_files.get(filename)
        self.date_fields = [f for f in fields if f.endswith("date")]

        bcpreader = bcp.DictReader(bcpfile, fieldnames=fields)
        for k, row in tqdm.tqdm(enumerate(bcpreader)):
            row = self.clean_fields(row)
            if not row.get("regno"):
                continue
            charity = self.get_charity(row['regno'])
            if (filename in ["extract_main_charity", "extract_charity"] and row.get("subno", '0') == '0'):
                for field in row:
                    charity[field] = row[field]
            else:
                charity[filename].append(row)
            self.set_charity(row['regno'], charity)

    def initialise_charities(self):
        self.aooref = AreaOfOperation.objects.all()
        self.aooref = {(a.aootype, a.aookey): a for a in self.aooref}

        if self.redis:
            return self.redis.delete('charities')
        self.charities = {}

    def get_charity(self, regno):
        if self.redis:
            charity = self.redis.hget('charities', regno)
            return pickle.loads(charity) if charity else {f: [] for f in self.ccew_files.keys()}
        return self.charities.get(regno, {f: [] for f in self.ccew_files.keys()})

    def set_charity(self, regno, charity):
        if self.redis:
            return self.redis.hset('charities', regno, pickle.dumps(charity))
        self.charities[regno] = charity

    def get_all_charities(self):
        if self.redis:
            for regno, charity in self.redis.hscan_iter('charities'):
                yield (regno.decode(), pickle.loads(charity))
        else:
            for regno, record in self.charities.items():
                yield (regno, record)

    def process_charities(self):
        
        for regno, record in self.get_all_charities():

            # helps with debugging - shouldn't normally be empty
            record["regno"] = regno

            # work out registration dates
            registration_date, removal_date = self.get_regdates(record)

            # work out org_types and org_ids
            org_types = [
                "Registered Charity",
                "Registered Charity (England and Wales)"
            ]
            org_ids = [self.get_org_id(record)]
            coyno = self.parse_company_number(record.get("coyno"))
            if coyno:
                org_types.append("Registered Company")
                org_types.append("Incorporated Charity")
                org_ids.append("GB-COH-{}".format(coyno))

            # check for CIOs
            if record.get("gd") and record["gd"].startswith("CIO - "):
                org_types.append("Charitable Incorporated Organisation")
                if record["gd"].lower().startswith("cio - association"):
                    org_types.append("Charitable Incorporated Organisation - Association")
                elif record["gd"].lower().startswith("cio - foundation"):
                    org_types.append("Charitable Incorporated Organisation - Foundation")
            org_types = [self.orgtype_cache[slugify(o)] for o in org_types]

            self.records.append(
                Organisation(**{
                    "org_id": self.get_org_id(record),
                    "name": self.parse_name(record.get("name")),
                    "charityNumber": record.get("regno"),
                    "companyNumber": coyno,
                    "streetAddress": record.get("add1"),
                    "addressLocality": record.get("add2"),
                    "addressRegion": record.get("add3"),
                    "addressCountry": record.get("add4"),
                    "postalCode": self.parse_postcode(record.get("postcode")),
                    "telephone": record.get("phone"),
                    "alternateName": [
                        self.parse_name(c["name"])
                        for c in record.get("extract_name", [])
                    ],
                    "email": record.get("email"),
                    "description": self.get_objects(record),
                    "organisationType": [o.slug for o in org_types],
                    "organisationTypePrimary": org_types[0],
                    "url": self.parse_url(record.get("web")),
                    "location": self.get_locations(record),
                    "latestIncome": int(record["income"]) if record.get("income") else None,
                    "latestIncomeDate": record["incomedate"] if record.get("incomedate") else None,
                    "dateModified": datetime.datetime.now(),
                    "dateRegistered": registration_date,
                    "dateRemoved": removal_date,
                    "active": record.get("orgtype") == "R",
                    "parent": None,
                    "orgIDs": org_ids,
                    "scrape": self.scrape,
                    "source": self.source,
                    "spider": self.name,
                    "org_id_scheme": self.orgid_scheme,
                })
            )
            self.object_count += 1

    def close_spider(self):
        super(Command, self).close_spider()
        self.records = None
        self.link_records = None

        # now start inserting charity records
        self.charity_count = 0
        self.logger.info("Inserting CharityRaw records")
        CharityRaw.objects.bulk_create(self.get_bulk_create())
        self.logger.info("Inserted {:,.0f} CharityRaw records inserted".format(self.charity_count))
        self.scrape.result['charity_records'] = self.charity_count
        self.scrape.save()

        self.logger.info("Deleting old CharityRaw records")
        CharityRaw.objects.filter(
            spider__exact=self.name,
        ).exclude(
            scrape_id=self.scrape.id,
        ).delete()
        self.logger.info("Old CharityRaw records deleted")

        # execute SQL statements
        with connection.cursor() as cursor:
            for sql_name, sql in UPDATE_CCEW.items():
                self.logger.info("Starting SQL: {}".format(sql_name))
                cursor.execute(sql)
                self.logger.info("Finished SQL: {}".format(sql_name))


    def get_bulk_create(self):

        for regno, record in tqdm.tqdm(self.get_all_charities()):
            self.charity_count += 1
            yield CharityRaw(
                org_id=self.get_org_id(record),
                data=record,
                scrape=self.scrape,
                spider=self.name,
            )


    def get_locations(self, record):
        # work out locations
        locations = []
        for l in record.get("extract_charity_aoo", []):
            aookey = (l["aootype"], l["aookey"])
            aoo = self.aooref.get(aookey)
            if not aoo:
                continue
            if aoo.GSS != "":
                locations.append({
                    "id": aoo["GSS"],
                    "name": aoo["aooname"],
                    "geoCode": aoo["GSS"],
                    "geoCodeType": AREA_TYPES.get(aoo["GSS"][0:3], "Unknown"),
                })
            elif aoo.get("ISO3166_1", "") != "":
                locations.append({
                    "id": aoo["ISO3166_1"],
                    "name": aoo["aooname"],
                    "geoCode": aoo["ISO3166_1"],
                    "geoCodeType": "ISO3166-1",
                })
        return locations

    def get_regdates(self, record):
        reg = [r for r in record.get("extract_registration", []) if r.get("regdate") and (r.get("subno") == '0')]
        reg = sorted(reg, key=lambda x: x.get("regdate"))
        if not reg:
            return (None, None)

        return (
            reg[0].get("regdate"),
            reg[-1].get("remdate")
        )

    def get_objects(self, record):
        objects = []
        for o in record.get("extract_objects", []):
            if o.get("subno") == '0' and isinstance(o['object'], str):
                objects.append(re.sub("[0-9]{4}$", "", o['object']))
        return ''.join(objects)
