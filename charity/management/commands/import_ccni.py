import datetime
from collections import defaultdict

import tqdm
from django.db import connection

from charity.management.commands._ccni_sql import UPDATE_CCNI
from charity.models import CharityRaw
from ftc.management.commands._base_scraper import CSVScraper
from ftc.models import Organisation


class Command(CSVScraper):
    name = 'ccni'
    allowed_domains = ['charitycommissionni.org.uk', 'gist.githubusercontent.com']
    start_urls = [
        "https://gist.githubusercontent.com/BobHarper1/2687545c562b47bc755aef2e9e0de537/raw/ac052c33fd14a08dd4c2a0604b54c50bc1ecc0db/ccni_extra",
        "https://www.charitycommissionni.org.uk/umbraco/api/charityApi/ExportSearchResultsToCsv/?include=Linked&include=Removed",
    ]
    org_id_prefix = "GB-NIC"
    id_field = "Reg charity number"
    date_fields = ["Date registered", "Date for financial year ending"]
    date_format = {
        "Date registered": "%d/%m/%Y",
        "Date for financial year ending": "%d %B %Y"
    }
    source = {
        "title": "Charity Commission for Northern Ireland charity search",
        "description": "",
        "identifier": "ccni",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Charity Commission for Northern Ireland",
            "website": "https://www.charitycommissionni.org.uk/",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "http://www.charitycommissionni.org.uk/charity-search/",
                "title": "Charity Commission for Northern Ireland charity search"
            }
        ],
    }
    orgtypes = [
        "Registered Charity",
        "Registered Charity (Northern Ireland)",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.raw_records = []

    def parse_row(self, record):

        record = self.clean_fields(record)

        if "Charity_number" in record:
            if not hasattr(self, "extra_names"):
                self.extra_names = defaultdict(list)
            self.extra_names[record['Charity_number']].append(record['Other_names'])
            return

        address, postcode = self.split_address(record.get("Public address", ""))

        org_types = [
            self.orgtype_cache["registered-charity"],
            self.orgtype_cache["registered-charity-northern-ireland"],
        ]

        org_ids = [self.get_org_id(record)]
        coyno = self.parse_company_number(record.get("Company number"))
        if coyno:
            company_type = self.add_org_type("Registered Company")
            org_types.append(company_type)
            org_ids.append("GB-COH-{}".format(coyno))

        self.raw_records.append({
            **record,
            "address": ", ".join([a for a in address if a]),
            "postcode": postcode,
        })

        self.add_org_record(
            Organisation(**{
                "org_id": self.get_org_id(record),
                "name": record.get("Charity name").replace("`", "'"),
                "charityNumber": "NIC{}".format(record.get(self.id_field)),
                "companyNumber": coyno,
                "streetAddress": address[0],
                "addressLocality": address[1],
                "addressRegion": address[2],
                "addressCountry": "Northern Ireland",
                "postalCode": postcode,
                "telephone": record.get("Telephone"),
                "alternateName": self.extra_names.get(record.get(self.id_field), []),
                "email": record.get("Email"),
                "description": None,
                "organisationType": [o.slug for o in org_types],
                "organisationTypePrimary": self.orgtype_cache['registered-charity'],
                "url": self.parse_url(record.get("Website")),
                "location": [],
                "latestIncome": int(record["Total income"]) if record.get("Total income") else None,
                "dateModified": datetime.datetime.now(),
                "dateRegistered": record.get("Date registered"),
                "dateRemoved": None,
                "active": record.get("Status") != "Removed",
                "parent": None,
                "orgIDs": org_ids,
                "scrape": self.scrape,
                "source": self.source,
                "spider": self.name,
                "org_id_scheme": self.orgid_scheme,
            })
        )

    def parse_company_number(self, coyno):
        if not coyno:
            return None

        coyno = coyno.strip()
        if coyno == "" or int(coyno) == 0 or int(coyno) == 999999:
            return None

        if coyno.isdigit():
            return "NI" + coyno.rjust(6, "0")

        return coyno

    def close_spider(self):
        super(Command, self).close_spider()
        self.records = None
        self.link_records = None

        # now start inserting charity records
        self.logger.info("Inserting CharityRaw records")
        CharityRaw.objects.bulk_create(self.get_bulk_create())
        self.logger.info("CharityRaw records inserted")

        self.logger.info("Deleting old CharityRaw records")
        CharityRaw.objects.filter(
            spider__exact=self.name,
        ).exclude(
            scrape_id=self.scrape.id,
        ).delete()
        self.logger.info("Old CharityRaw records deleted")

        # execute SQL statements
        with connection.cursor() as cursor:
            for sql_name, sql in UPDATE_CCNI.items():
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
