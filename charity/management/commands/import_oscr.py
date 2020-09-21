import csv
import datetime
import io
import zipfile

import tqdm
from django.db import connection

from charity.management.commands._oscr_sql import UPDATE_OSCR
from charity.models import CharityRaw
from ftc.management.commands._base_scraper import CSVScraper
from ftc.models import Organisation


class Command(CSVScraper):
    name = "oscr"
    allowed_domains = ["oscr.org.uk", "githubusercontent.com"]
    start_urls = [
        "https://www.oscr.org.uk/umbraco/Surface/FormsSurface/CharityRegDownload",
        "https://www.oscr.org.uk/umbraco/Surface/FormsSurface/CharityFormerRegDownload",
    ]
    org_id_prefix = "GB-SC"
    id_field = "Charity Number"
    date_fields = ["Registered Date", "Year End", "Ceased Date"]
    date_format = {
        "Registered Date": "%d/%m/%Y %H:%M",
        "Ceased Date": "%d/%m/%Y %H:%M",
        "Year End": "%d/%m/%Y",
    }
    source = {
        "title": "Office of Scottish Charity Regulator Charity Register Download",
        "description": "",
        "identifier": "oscr",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/",
        "license_name": "Open Government Licence v2.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Office of Scottish Charity Regulator",
            "website": "https://www.oscr.org.uk/",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "",
                "title": "Office of Scottish Charity Regulator Charity Register Download",
            }
        ],
    }
    orgtypes = [
        "Registered Charity",
        "Registered Charity (Scotland)",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.raw_records = []

    def parse_file(self, response, source_url):
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            for f in z.infolist():
                self.logger.info("Opening: {}".format(f.filename))
                with z.open(f) as csvfile:
                    reader = csv.DictReader(io.TextIOWrapper(csvfile, encoding="utf8"))
                    rowcount = 0
                    for row in reader:
                        rowcount += 1

                        self.parse_row(row)

    def parse_row(self, record):

        record = self.clean_fields(record)

        address, _ = self.split_address(
            record.get("Principal Office/Trustees Address", ""), get_postcode=False
        )

        org_types = [
            self.orgtype_cache["registered-charity"],
            self.orgtype_cache["registered-charity-scotland"],
        ]
        if record.get("Regulatory Type") != "Standard" and record.get(
            "Regulatory Type"
        ):
            org_types.append(self.add_org_type(record.get("Regulatory Type")))
        if record.get("Designated religious body") == "Yes":
            org_types.append(self.add_org_type("Designated religious body"))

        if (
            record.get("Constitutional Form")
            == "SCIO (Scottish Charitable Incorporated Organisation)"
        ):
            org_types.append(
                self.add_org_type("Scottish Charitable Incorporated Organisation")
            )
        elif (
            record.get("Constitutional Form")
            == "CIO (Charitable Incorporated Organisation, E&W)"
        ):
            org_types.append(self.add_org_type("Charitable Incorporated Organisation"))
        elif (
            record.get("Constitutional Form")
            == "Company (the charity is registered with Companies House)"
        ):
            org_types.append(self.add_org_type("Registered Company"))
            org_types.append(self.add_org_type("Incorporated Charity"))
        elif (
            record.get("Constitutional Form")
            == "Trust (founding document is a deed of trust) (other than educational endowment)"
        ):
            org_types.append(self.add_org_type("Trust"))
        elif record.get("Constitutional Form") != "Other" and record.get(
            "Constitutional Form"
        ):
            org_types.append(self.add_org_type(record.get("Constitutional Form")))

        org_ids = [self.get_org_id(record)]

        self.raw_records.append(record)

        self.records.append(
            Organisation(
                **{
                    "org_id": self.get_org_id(record),
                    "name": record.get("Charity Name"),
                    "charityNumber": record.get(self.id_field),
                    "companyNumber": None,
                    "streetAddress": address[0],
                    "addressLocality": address[1],
                    "addressRegion": address[2],
                    "addressCountry": "Scotland",
                    "postalCode": self.parse_postcode(record.get("Postcode")),
                    "telephone": None,
                    "alternateName": [record.get("Known As")]
                    if record.get("Known As")
                    else [],
                    "email": None,
                    "description": record.get("Objectives"),
                    "organisationType": [o.slug for o in org_types],
                    "organisationTypePrimary": org_types[0],
                    "url": self.parse_url(record.get("Website")),
                    "location": [],
                    "latestIncome": int(record["Most recent year income"])
                    if record.get("Most recent year income")
                    else None,
                    "dateModified": datetime.datetime.now(),
                    "dateRegistered": record.get("Registered Date"),
                    "dateRemoved": record.get("Ceased Date"),
                    "active": record.get("Charity Status") != "Removed",
                    "parent": record.get(
                        "Parent Charity Name"
                    ),  # @TODO: More sophisticated getting of parent charities here
                    "orgIDs": org_ids,
                    "scrape": self.scrape,
                    "source": self.source,
                    "spider": self.name,
                    "org_id_scheme": self.orgid_scheme,
                }
            )
        )

    def close_spider(self):
        super(Command, self).close_spider()
        self.records = None
        self.link_records = None

        # now start inserting charity records
        self.logger.info("Inserting CharityRaw records")
        CharityRaw.objects.bulk_create(self.get_bulk_create())
        self.logger.info("CharityRaw records inserted")

        self.logger.info("Deleting old CharityRaw records")
        CharityRaw.objects.filter(spider__exact=self.name,).exclude(
            scrape_id=self.scrape.id,
        ).delete()
        self.logger.info("Old CharityRaw records deleted")

        # execute SQL statements
        with connection.cursor() as cursor:
            for sql_name, sql in UPDATE_OSCR.items():
                self.logger.info("Starting SQL: {}".format(sql_name))
                cursor.execute(sql)
                self.logger.info("Finished SQL: {}".format(sql_name))

    def get_bulk_create(self):

        for record in tqdm.tqdm(self.raw_records):
            yield CharityRaw(
                org_id=self.get_org_id(record),
                data=record,
                scrape=self.scrape,
                spider=self.name,
            )
