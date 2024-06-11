import datetime
import io

from openpyxl import load_workbook

from ftc.management.commands._base_scraper import HTMLScraper
from ftc.models import Organisation


class Command(HTMLScraper):
    """
    Spider for scraping details of Churches in England from the Church of England "Open Church Codes" page
    """

    name = "coe"
    allowed_domains = ["churchofengland.org"]
    start_urls = [
        "https://www.churchofengland.org/resources/churchcare/churchcare-grants/open-grant-data-360-giving",
    ]
    org_id_prefix = "GB-COE"
    id_field = "church code"
    source = {
        "title": "Churches in England",
        "description": (
            "A list of all open-for-worship churches is available. Covers England"
        ),
        "identifier": "coe",
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "license_name": "Creative Commons Attribution 4.0 International License",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Church of England",
            "website": "https://www.churchofengland.org/",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "https://www.churchofengland.org/resources/churchcare/churchcare-grants/open-grant-data-360-giving",
                "title": "All open-for-worship churches",
            }
        ],
    }
    orgtypes = ["Church"]
    date_fields = []
    date_format = "%d/%m/%Y"

    def parse_file(self, response, source_url):
        for link in response.html.find("a"):
            if link.text.strip() == "Open Church Codes":
                link = response.html._make_absolute(link.attrs.get("href"))
                self.logger.info("Fetching file: {}".format(link))
                self.set_download_url(link)
                self.fetch_link(link)

    def fetch_link(self, link):
        self.set_download_url(link)
        r = self.session.get(link)
        r.raise_for_status()

        wb = load_workbook(io.BytesIO(r.content), read_only=True)
        latest_sheet = wb.active

        self.logger.info("Latest sheet: {}".format(latest_sheet.title))
        headers = []
        for k, row in enumerate(latest_sheet.rows):
            if not row[0].value:
                continue

            if not headers:
                headers = [c.value.lower() for c in row]
            else:
                record = dict(zip(headers, [c.value for c in row]))
                self.parse_row(record)

    def parse_row(self, record):
        record = self.clean_fields(record)
        if not record.get("church name") or not record.get("church code"):
            return

        org_types = [
            self.add_org_type("Church"),
        ]
        if record.get("type"):
            org_types.append(self.add_org_type(record["type"]))

        org_ids = [self.get_org_id(record)]

        description = """
- Diocese: {diocese_name} ({diocese_number})
- Archdeaconry: {archdeaconry_name} ({archdeaconry_id})
- Deanery: {deanery_name} ({deanery_id})
- Benefice: {benefice_name} ({benefice_code})
- Parish: {parish_name} ({parish_code})
""".format(**{k.replace(" ", "_"): v for k, v in record.items()})

        self.add_org_record(
            Organisation(
                **{
                    "org_id": self.get_org_id(record),
                    "name": record.get("church name"),
                    "charityNumber": None,
                    "companyNumber": None,
                    "streetAddress": None,
                    "addressLocality": None,
                    "addressRegion": None,
                    "addressCountry": "England",
                    "postalCode": None,
                    "telephone": None,
                    "alternateName": [],
                    "email": None,
                    "description": description,
                    "organisationType": [o.slug for o in org_types],
                    "organisationTypePrimary": org_types[0],
                    "url": None,
                    # "location": locations,
                    "latestIncome": None,
                    "dateModified": datetime.datetime.now(),
                    "dateRegistered": None,
                    "dateRemoved": None,
                    "active": True,
                    "parent": None,
                    "orgIDs": org_ids,
                    "scrape": self.scrape,
                    "source": self.source,
                    "spider": self.name,
                    "org_id_scheme": self.orgid_scheme,
                }
            )
        )
