import csv
import datetime
import io

from ftc.management.commands._base_scraper import CSVScraper
from ftc.models import Organisation


class Command(CSVScraper):
    name = "hesa"
    allowed_domains = ["hesa.ac.uk"]
    start_urls = [
        "https://www.hesa.ac.uk/collection/provider-tools/all_hesa_providers?ProviderAllHESAEnhanced.csv",
    ]
    org_id_prefix = "GB-HESA"
    source = {
        "title": "Higher Education Statistics Agency",
        "description": "Higher Education Statistics Agency - we are the experts in UK higher education data and analysis, and the designated data body for England. We collect, process, and publish data about higher education (HE) in the UK. As the trusted source of HE data and analysis, we play a key role in supporting and enhancing the competitive strength of the sector.",
        "identifier": "hesa",
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "license_name": "Creative Commons Attribution 4.0 International Licence",
        "issued": "",
        "modified": "",
        "publisher": {"name": "HESA", "website": "https://www.hesa.ac.uk/"},
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "https://www.hesa.ac.uk/collection/provider-tools/all_hesa_providers",
                "title": "HESA - Higher education providers",
            }
        ],
    }
    orgtypes = ["Higher Education Institution", "University"]

    def parse_file(self, response, source_url):
        try:
            csv_text = response.text
        except AttributeError:
            csv_text = response.body.decode(self.encoding)

        with io.StringIO(csv_text) as a:
            csvreader = csv.DictReader(
                a,
                fieldnames=[
                    "INSTID",
                    "UKPRN",
                    "ProviderName",
                    "CountryCode",
                    "CategoryName",
                    "FE_Provider",
                    "Rescinded",
                ],
            )
            for k, row in enumerate(csvreader):
                self.parse_row(row)

    def parse_row(self, record):
        record = self.clean_fields(record)
        orgids = [
            "-".join([self.org_id_prefix, str(record["INSTID"])]),
        ]
        if record["UKPRN"]:
            orgids.append("-".join(["GB-UKPRN", str(record["UKPRN"])]))

        org_types = [
            self.orgtype_cache["higher-education-institution"],
            self.orgtype_cache["university"],
        ]

        fe_provider = record.get("FE_Provider")
        if fe_provider and fe_provider.strip().lower() == "yes":
            org_types.append(self.add_org_type("Further Education Provider"))

        self.add_org_record(
            Organisation(
                **{
                    "org_id": orgids[0],
                    "name": record["ProviderName"],
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
                    "organisationType": [o.slug for o in org_types],
                    "organisationTypePrimary": org_types[0],
                    "url": None,
                    "latestIncome": None,
                    "dateModified": datetime.datetime.now(),
                    "dateRegistered": None,
                    "dateRemoved": None,
                    "active": True,
                    "parent": None,
                    "orgIDs": orgids,
                    "scrape": self.scrape,
                    "source": self.source,
                    "spider": self.name,
                    "org_id_scheme": self.orgid_scheme,
                }
            )
        )
