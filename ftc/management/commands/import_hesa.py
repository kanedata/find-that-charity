import datetime
import io
from collections import defaultdict

from django.utils.text import slugify
from openpyxl import load_workbook

from ftc.management.commands._base_scraper import HTMLScraper
from ftc.models import Organisation


class Command(HTMLScraper):
    name = "hesa"
    allowed_domains = ["hesa.ac.uk"]
    start_urls = [
        "https://www.hesa.ac.uk/support/providers",
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
                "accessURL": "",
                "title": "HESA - Higher education providers",
            }
        ],
    }
    orgtypes = ["Higher Education"]
    hesa_org_types = {
        "HEI": "University",
        "FEC": "Further Education College",
        "AP": "Alternative Provider",
    }

    def parse_file(self, response, source_url):
        files = [link for link in response.html.links if link.endswith(".xlsx")]
        self.set_download_url(source_url)

        records = defaultdict(dict)
        for link in files:
            r = self.session.get(link)
            r.raise_for_status()

            wb = load_workbook(io.BytesIO(r.content), read_only=True)
            ws = wb.active

            headers = None
            for k, row in enumerate(ws.rows):
                if not headers:
                    headers = [slugify(c.value) for c in row]
                else:
                    record = dict(zip(headers, [c.value for c in row]))
                    for k, v in record.items():
                        records[record["instid"]][k] = v

        for r in records.values():
            self.parse_row(r)

    def parse_row(self, record):

        orgids = [
            "-".join([self.org_id_prefix, str(record["instid"])]),
            "-".join(["GB-UKPRN", str(record["ukprn"])]),
        ]

        org_types = [
            self.orgtype_cache["higher-education"],
        ]

        self.records.append(
            Organisation(
                **{
                    "org_id": orgids[0],
                    "name": record["provider-name"],
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
                    "location": [],
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
