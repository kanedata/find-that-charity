import csv
import datetime
import io
import json
import zipfile

from ftc.management.commands._base_scraper import HTMLScraper
from ftc.models import Organisation


class Command(HTMLScraper):
    name = 'nhsods'
    allowed_domains = ['nhs.uk']
    start_urls = ['https://digital.nhs.uk/services/organisation-data-service/data-downloads']
    org_id_prefix = "GB-NHS"
    id_field = "Code"
    date_fields = ["Open Date", "Close Date", "Join Parent Date", "Left Parent Date"]
    date_format = "%Y%m%d"
    source = {
        "title": "NHS Organisation Data Service downloads",
        "description": "",
        "identifier": "nhsods",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "NHS Digital",
            "website": "https://digital.nhs.uk/",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "http://www.charitycommissionni.org.uk/charity-search/",
                "title": "Charity Commission for Northern Ireland charity search"
            }
        ],
    }
    zipfiles = [
        # {"org_type": "NHS England Commissioning and Government Office Regions", "url": "https://files.digital.nhs.uk/assets/ods/current/eauth.zip"},
        {"org_type": "Special Health Authorities", "url": "https://files.digital.nhs.uk/assets/ods/current/espha.zip"},
        {"org_type": "Commissioning Support Units", "url": "https://files.digital.nhs.uk/assets/ods/current/ecsu.zip"},
        # {"org_type": "Commissioning Support Units sites", "url": "https://files.digital.nhs.uk/assets/ods/current/ecsusite.zip"},
        # {"org_type": "Executive Agency Programme", "url": "https://files.digital.nhs.uk/assets/ods/current/eother.zip"},
        {"org_type": "NHS Support Agencies and Shared Services", "url": "https://files.digital.nhs.uk/assets/ods/current/ensa.zip"},
        {"org_type": "GP practices", "url": "https://files.digital.nhs.uk/assets/ods/current/epraccur.zip"},
        {"org_type": "Clinical Commissioning Groups", "url": "https://files.digital.nhs.uk/assets/ods/current/eccg.zip"},
        # {"org_type": "Clinical Commissioning Group sites", "url": "https://files.digital.nhs.uk/assets/ods/current/eccgsite.zip"},
        {"org_type": "NHS Trusts", "url": "https://files.digital.nhs.uk/assets/ods/current/etr.zip"},
        # {"org_type": "NHS Trust sites", "url": "https://files.digital.nhs.uk/assets/ods/current/ets.zip"},
        # {"org_type": "NHS Trusts and sites", "url": "https://files.digital.nhs.uk/assets/ods/current/etrust.zip"},
        {"org_type": "Care Trusts", "url": "https://files.digital.nhs.uk/assets/ods/current/ect.zip"},
        # {"org_type": "Care Trust sites", "url": "https://files.digital.nhs.uk/assets/ods/current/ectsite.zip"},
        # {"org_type": "Care Trusts and sites", "url": "https://files.digital.nhs.uk/assets/ods/current/ecare.zip"},
        {"org_type": "Welsh Local Health Boards", "url": "https://files.digital.nhs.uk/assets/ods/current/wlhb.zip"},
        # {"org_type": "Welsh Local Health Board sites", "url": "https://files.digital.nhs.uk/assets/ods/current/wlhbsite.zip"},
        # {"org_type": "Welsh Local Health Boards and sites", "url": "https://files.digital.nhs.uk/assets/ods/current/whbs.zip"},
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
    orgtypes = ['Health']

    def fetch_file(self):
        self.files = {}
        for u in self.zipfiles:
            r = self.session.get(u['url'])
            self.files[u['org_type']] = r

        # self.source["distribution"] = [{
        #     "downloadURL": f["url"],
        #     "accessURL": self.start_urls[0],
        #     "title": "NHS Digital Organisation Data Service - {}".format(f["org_type"])
        # } for f in self.files]
        # self.source["modified"] = datetime.datetime.now().isoformat()


    def parse_file(self, response, org_type):
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            for f in z.infolist():
                if not f.filename.endswith(".csv"):
                    continue
                print("Opening: {}".format(f.filename))
                with z.open(f) as csvfile:
                    reader = csv.DictReader(io.TextIOWrapper(csvfile), fieldnames=self.fields)
                    rowcount = 0
                    for row in reader:
                        rowcount += 1

                        self.parse_row(row, org_type)

    def parse_row(self, record, org_type=None):

        record = self.clean_fields(record)

        org_types = [
            self.orgtype_cache['health']
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
                address["addressLocality"] += ", {}".format(record.get("Address Line 4"))
            else:
                address["addressLocality"] = record.get("Address Line 4")

        self.records.append(
            Organisation(**{
                "org_id": self.get_org_id(record),
                "name": self.parse_name(record.get("Name")),
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
                "location": [],
                "latestIncome": None,
                "dateModified": datetime.datetime.now(),
                "dateRegistered": record.get("Open Date"),
                "dateRemoved": record.get("Close Date"),
                "active": record.get("Close Date") is None,
                "parent": record.get("Parent Organisation Code"),
                "orgIDs": [self.get_org_id(record)],
                "scrape": self.scrape,
                "source": self.source,
                "spider": self.name,
            })
        )
