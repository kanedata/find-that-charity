import datetime

from ftc.management.commands._base_scraper import CSVScraper
from ftc.models import Organisation


class Command(CSVScraper):
    help = "Import Government Organisations Register"
    name = "gor"
    allowed_domains = ["register.gov.uk"]
    start_urls = [
        "https://government-organisation.register.gov.uk/records.csv?page-size=5000"
    ]
    org_id_prefix = "GB-GOR"
    id_field = "key"
    date_fields = ["entry-timestamp", "start-date", "end-date"]
    date_format = {
        "entry-timestamp": "%Y-%m-%dT%H:%M:%SZ",
        "start-date": "%Y-%m-%d",
        "end-date": "%Y-%m-%d",
    }
    source = {
        "title": "Government organisations on GOV.UK register",
        "description": "Government departments, agencies or teams that are on the GOV.UK website",
        "identifier": "gor",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Cabinet Office",
            "website": "https://www.gov.uk/government/organisations/cabinet-office",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "https://www.registers.service.gov.uk/registers/government-organisation/",
                "title": "Government organisations on GOV.UK register",
            }
        ],
    }
    orgtypes = ["Government Organisation"]

    def parse_row(self, record):

        record = self.clean_fields(record)
        self.records.append(
            Organisation(
                **{
                    "org_id": self.get_org_id(record),
                    "name": record.get("name"),
                    "charityNumber": None,
                    "companyNumber": None,
                    "streetAddress": None,
                    "addressLocality": None,
                    "addressRegion": None,
                    "addressCountry": None,
                    "postalCode": None,
                    "telephone": None,
                    "alternateName": [],
                    "email": None,
                    "description": None,
                    "organisationType": list(self.orgtype_cache.keys()),
                    "organisationTypePrimary": self.orgtype_cache[
                        "government-organisation"
                    ],
                    "url": record.get("website"),
                    "latestIncome": None,
                    "dateModified": datetime.datetime.now(),
                    "dateRegistered": record.get("start-date"),
                    "dateRemoved": record.get("end-date"),
                    "active": record.get("end-date") is None,
                    "parent": None,
                    "orgIDs": [self.get_org_id(record)],
                    "scrape": self.scrape,
                    "source": self.source,
                    "spider": self.name,
                    "org_id_scheme": self.orgid_scheme,
                }
            )
        )
