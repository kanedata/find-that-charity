import datetime

from ftc.management.commands._base_scraper import CSVScraper
from ftc.management.commands.import_lae import LA_TYPES
from ftc.models import Organisation


class Command(CSVScraper):
    name = 'lani'
    allowed_domains = ['register.gov.uk']
    start_urls = [
        "https://local-authority-nir.register.gov.uk/records.csv?page-size=5000"
    ]
    org_id_prefix = "GB-LANI"
    id_field = "key"
    date_fields = ["entry-timestamp", "start-date", "end-date"]
    date_format = {
        "entry-timestamp": "%Y-%m-%dT%H:%M:%SZ",
        "start-date": "%Y-%m-%d",
        "end-date": "%Y-%m-%d",
    }
    source = {
        "title": "Local authorites in Northern Ireland register",
        "description": "Local authorities in Northern Ireland",
        "identifier": "lani",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Department for Communities (Northern Ireland)",
            "website": "https://www.communities-ni.gov.uk/",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "https://www.registers.service.gov.uk/registers/local-authority-nir/",
                "title": "Local authorites in Northern Ireland register"
            }
        ],
    }
    orgtypes = ['Local Authority']

    def parse_row(self, record):

        record = self.clean_fields(record)

        org_types = [
            self.orgtype_cache["local-authority"],
        ]

        if record.get('local-authority-type'):
            org_types.append(
                self.add_org_type(LA_TYPES.get(record.get(
                "local-authority-type"), record.get("local-authority-type")))
            )
        org_ids = [self.get_org_id(record)]

        locations = []
        # @TODO: map local authority code to GSS to add locations

        self.records.append(
            Organisation(**{
                "org_id": self.get_org_id(record),
                "name": record.get("name"),
                "charityNumber": None,
                "companyNumber": None,
                "streetAddress": None,
                "addressLocality": None,
                "addressRegion": None,
                "addressCountry": "Northern Ireland",
                "postalCode": None,
                "telephone": None,
                "alternateName": [],
                "email": None,
                "description": None,
                "organisationType": [o.slug for o in org_types],
                "organisationTypePrimary": org_types[0],
                "url": record.get("website"),
                "location": locations,
                "latestIncome": None,
                "dateModified": datetime.datetime.now(),
                "dateRegistered": record.get("start-date"),
                "dateRemoved": record.get("end-date"),
                "active": record.get("end-date") is None,
                "parent": None,
                "orgIDs": org_ids,
                "scrape": self.scrape,
                "source": self.source,
                "spider": self.name,
            })
        )
