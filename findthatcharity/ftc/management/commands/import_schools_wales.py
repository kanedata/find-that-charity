# -*- coding: utf-8 -*-
import datetime
import io

from pyexcel_ods3 import get_data

from ftc.management.commands._base_scraper import AREA_TYPES, HTMLScraper
from ftc.models import Organisation

WAL_LAS = {
    "Blaenau Gwent": "W06000019",
    "Bridgend": "W06000013",
    "Caerphilly": "W06000018",
    "Cardiff": "W06000015",
    "Carmarthenshire": "W06000010",
    "Ceredigion": "W06000008",
    "Conwy": "W06000003",
    "Denbighshire": "W06000004",
    "Flintshire": "W06000005",
    "Gwynedd": "W06000002",
    "Isle of Anglesey": "W06000001",
    "Merthyr Tydfil": "W06000024",
    "Monmouthshire": "W06000021",
    "Neath Port Talbot": "W06000012",
    "Newport": "W06000022",
    "Pembrokeshire": "W06000009",
    "Powys": "W06000023",
    "Rhondda Cynon Taf": "W06000016",
    "Swansea": "W06000011",
    "The Vale of Glamorgan": "W06000014",
    "Torfaen": "W06000020",
    "Wrexham": "W06000006",
}


class Command(HTMLScraper):
    name = 'schools_wales'
    allowed_domains = ['gov.wales']
    start_urls = ["https://gov.wales/address-list-schools"]
    org_id_prefix = "GB-WALEDU"
    id_field = "School Number"
    date_fields = []
    source = {
        "title": "Address list of schools",
        "description": "",
        "identifier": "walesschools",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Welsh Government",
            "website": "https://gov.wales/",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "",
                "title": "Address list of schools"
            }
        ],
    }
    orgtypes = ['Education']

    def parse_file(self, response, source_url):
        link = list(response.html.find("div.document", first=True).absolute_links)[0]
        self.logger.info("Using url {}".format(link))
        # self.source["distribution"][0]["downloadURL"] = link
        # self.source["distribution"][0]["accessURL"] = self.start_urls[0]
        # self.source["modified"] = datetime.datetime.now().isoformat()
        r = self.session.get(link)

        wb = get_data(io.BytesIO(r.content))
        for sheet in ['Maintained', 'Independent', 'PRU']:
            headers = wb[sheet][0]
            data = wb[sheet][1:]
            for k, row in enumerate(data):

                row = dict(zip(headers, row))
                row["type"] = sheet
                self.parse_row(row)

    def parse_row(self, record):

        record = self.clean_fields(record)

        address4 = ", ".join([
            record.get("Address {}".format(f))
            for f in [3, 4]
            if record.get("Address {}".format(f))
        ])
        org_types = self.get_org_types(record)

        if not record.get("School Name"):
            return

        self.records.append(
            Organisation(**{
                "org_id": self.get_org_id(record),
                "name": record.get("School Name"),
                "charityNumber": None,
                "companyNumber": None,
                "streetAddress": record.get("Address 1"),
                "addressLocality": record.get("Address 2"),
                "addressRegion": address4,
                "addressCountry": "Wales",
                "postalCode": self.parse_postcode(record.get("Postcode")),
                "telephone": record.get("Phone Number"),
                "alternateName": [],
                "email": None,
                "description": None,
                "organisationType": [o.slug for o in org_types],
                "organisationTypePrimary": org_types[0],
                "url": None,
                "location": self.get_locations(record),
                "latestIncome": None,
                "dateModified": datetime.datetime.now(),
                "dateRegistered": None,
                "dateRemoved": None,
                "active": True,
                "parent": None,
                "orgIDs": [self.get_org_id(record)],
                "scrape": self.scrape,
                "source": self.source,
                "spider": self.name,
                "org_id_scheme": self.orgid_scheme,
            })
        )

    def get_org_types(self, record):
        org_types = []
        for f in ["Sector", "Governance - see notes", "Welsh Medium Type - see notes", "School Type", "type"]:
            if record.get(f):
                if record.get(f) == "PRU":
                    org_types.append(self.add_org_type("Pupil Referral Unit"))
                else:
                    org_types.append(self.add_org_type(record[f] + " School"))
        org_types.append(self.add_org_type("Education"))
        return org_types

    def get_locations(self, record):
        locations = []
        if WAL_LAS.get(record.get("Local Authority")):
            code = WAL_LAS.get(record.get("Local Authority"))
            locations.append({
                "id": code,
                "name": record.get("Local Authority"),
                "geoCode": code,
                "geoCodeType": AREA_TYPES.get(code[0:3], "Local Authority"),
            })
        return locations
