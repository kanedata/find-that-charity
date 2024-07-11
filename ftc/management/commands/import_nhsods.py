import copy
import csv
import datetime
import io
import zipfile

from ftc.management.commands._base_scraper import HTMLScraper
from ftc.models import Organisation, Source


class Command(HTMLScraper):
    name = "nhsods"
    allowed_domains = ["nhs.uk"]
    start_urls = [
        "https://digital.nhs.uk/services/organisation-data-service/data-downloads"
    ]
    org_id_prefix = "GB-NHS"
    id_field = "Code"
    date_fields = ["Open Date", "Close Date", "Join Parent Date", "Left Parent Date"]
    date_format = "%Y%m%d"
    source_template = {
        "title": "NHS Organisation Data Service downloads",
        "description": "",
        "identifier": "nhsods",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {"name": "NHS Digital", "website": "https://digital.nhs.uk/"},
        "distribution": [{"downloadURL": "", "accessURL": "", "title": ""}],
    }
    zipfiles = [
        # {
        #   "org_type": "NHS England Commissioning and Government Office Regions",
        #   "url": "https://files.digital.nhs.uk/assets/ods/current/eauth.zip",
        #   "id": "eauth",
        # },
        {
            "org_type": "Special Health Authority",
            "url": "https://files.digital.nhs.uk/assets/ods/current/espha.zip",
            "id": "espha",
        },
        {
            "org_type": "Commissioning Support Unit",
            "url": "https://files.digital.nhs.uk/assets/ods/current/ecsu.zip",
            "id": "ecsu",
        },
        # {
        #   "org_type": "Commissioning Support Units sites",
        #   "url": "https://files.digital.nhs.uk/assets/ods/current/ecsusite.zip",
        #   "id": "ecsusite",
        # },
        # {
        #   "org_type": "Executive Agency Programme",
        #   "url": "https://files.digital.nhs.uk/assets/ods/current/eother.zip",
        #   "id": "eother",
        # },
        {
            "org_type": "NHS Support Agency or Shared Service",
            "url": "https://files.digital.nhs.uk/assets/ods/current/ensa.zip",
            "id": "ensa",
        },
        {
            "org_type": "GP practice",
            "url": "https://files.digital.nhs.uk/assets/ods/current/epraccur.zip",
            "id": "epraccur",
        },
        {
            "org_type": "Clinical Commissioning Group",
            "url": "https://files.digital.nhs.uk/assets/ods/current/eccg.zip",
            "id": "eccg",
        },
        # {
        #   "org_type": "Clinical Commissioning Group sites",
        #   "url": "https://files.digital.nhs.uk/assets/ods/current/eccgsite.zip"
        #   "id": "eccgsite",
        # },
        {
            "org_type": "NHS Trust",
            "url": "https://files.digital.nhs.uk/assets/ods/current/etr.zip",
            "id": "etr",
        },
        # {
        #   "org_type": "NHS Trust sites",
        #   "url": "https://files.digital.nhs.uk/assets/ods/current/ets.zip"
        #   "id": "ets",
        # },
        # {
        #   "org_type": "NHS Trusts and sites",
        #   "url": "https://files.digital.nhs.uk/assets/ods/current/etrust.zip"
        #   "id": "etrust",
        # },
        {
            "org_type": "Care Trust",
            "url": "https://files.digital.nhs.uk/assets/ods/current/ect.zip",
            "id": "ect",
        },
        # {
        #   "org_type": "Care Trust sites",
        #   "url": "https://files.digital.nhs.uk/assets/ods/current/ectsite.zip"
        #   "id": "ectsite",
        # },
        # {
        #   "org_type": "Care Trusts and sites",
        #   "url": "https://files.digital.nhs.uk/assets/ods/current/ecare.zip"
        #   "id": "ecare",
        # },
        {
            "org_type": "Welsh Local Health Board",
            "url": "https://files.digital.nhs.uk/assets/ods/current/wlhb.zip",
            "id": "wlhb",
        },
        # {
        #   "org_type": "Welsh Local Health Board sites",
        #   "url": "https://files.digital.nhs.uk/assets/ods/current/wlhbsite.zip"
        #   "id": "wlhbsite",
        # },
        # {
        #   "org_type": "Welsh Local Health Boards and sites",
        #   "url": "https://files.digital.nhs.uk/assets/ods/current/whbs.zip"
        #   "id": "whbs",
        # },
    ]
    fields = [
        "Code",
        "Name",
        "National Grouping",
        "High Level Health Geography",
        "Address Line 1",
        "Address Line 2",
        "Address Line 3",
        "Address Line 4",
        "Address Line 5",
        "Postcode",
        "Open Date",
        "Close Date",
        "column-13",
        "Organisation Sub-Type Code",
        "Parent Organisation Code",
        "Join Parent Date",
        "Left Parent Date",
        "Contact Telephone Number",
        "column-19",
        "column-20",
        "column-21",
        "Amended record indicator",
        "column-23",
        "column-24",
        "column-25",
        "column-26",
        "column-27",
    ]
    orgtypes = ["Health organisation", "NHS organisation"]

    def fetch_file(self):
        self.files = {}
        self.sources = {}
        for u in self.zipfiles:
            r = self.session.get(u["url"])
            r.raise_for_status()
            self.files[u["org_type"]] = r

            source = copy.deepcopy(self.source_template)
            source["distribution"] = [
                {
                    "downloadURL": u["url"],
                    "accessURL": self.start_urls[0],
                    "title": u["org_type"],
                }
            ]
            source["title"] = u["org_type"]
            source["modified"] = datetime.datetime.now().isoformat()
            self.sources[u["org_type"]], _ = Source.objects.update_or_create(
                id=f"{source['identifier']}-{u['id']}", defaults={"data": source}
            )

    def parse_file(self, response, org_type):
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            for f in z.infolist():
                if not f.filename.endswith(".csv"):
                    continue
                self.logger.info("Opening: {}".format(f.filename))
                with z.open(f) as csvfile:
                    reader = csv.DictReader(
                        io.TextIOWrapper(csvfile), fieldnames=self.fields
                    )
                    rowcount = 0
                    for row in reader:
                        rowcount += 1

                        self.parse_row(row, org_type)

    def parse_row(self, record, org_type=None):
        record = self.clean_fields(record)

        org_types = [
            self.orgtype_cache["health-organisation"],
            self.orgtype_cache["nhs-organisation"],
        ]
        if org_type:
            o = self.add_org_type(org_type)
            org_types.append(o)

        address = {
            "streetAddress": record.get("Address Line 1"),
            "addressLocality": record.get("Address Line 3"),
            "addressRegion": record.get("Address Line 5"),
            "addressCountry": None,
        }
        if record.get("Address Line 2"):
            if address["streetAddress"]:
                address["streetAddress"] += ", {}".format(record.get("Address Line 2"))
            else:
                address["streetAddress"] = record.get("Address Line 2")
        if record.get("Address Line 4"):
            if address["addressLocality"]:
                address["addressLocality"] += ", {}".format(
                    record.get("Address Line 4")
                )
            else:
                address["addressLocality"] = record.get("Address Line 4")

        parent = None
        if record.get("Parent Organisation Code"):
            parent = f"{self.org_id_prefix}-{record.get('Parent Organisation Code')}"

        self.add_org_record(
            Organisation(
                **{
                    "org_id": self.get_org_id(record),
                    "name": record.get("Name"),
                    "charityNumber": None,
                    "companyNumber": None,
                    "streetAddress": address["streetAddress"],
                    "addressLocality": address["addressLocality"],
                    "addressRegion": address["addressRegion"],
                    "addressCountry": address["addressCountry"],
                    "postalCode": record.get("Postcode"),
                    "telephone": record.get("Contact Telephone Number"),
                    "alternateName": [],
                    "email": None,
                    "description": None,
                    "organisationType": [o.slug for o in org_types],
                    "organisationTypePrimary": org_types[0],
                    "url": None,
                    "latestIncome": None,
                    "dateModified": datetime.datetime.now(),
                    "dateRegistered": record.get("Open Date"),
                    "dateRemoved": record.get("Close Date"),
                    "active": record.get("Close Date") is None,
                    "parent": parent,
                    "orgIDs": [self.get_org_id(record)],
                    "scrape": self.scrape,
                    "source": self.sources[org_type],
                    "spider": self.name,
                    "org_id_scheme": self.orgid_scheme,
                }
            )
        )
