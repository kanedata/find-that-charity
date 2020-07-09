import datetime
import re

from requests_html import HTMLSession
import requests_cache

from ftc.management.commands._base_scraper import AREA_TYPES, CSVScraper
from ftc.models import Organisation

REGION_CONVERT = {
    "A": "E12000001",
    "B": "E12000002",
    "D": "E12000003",
    "E": "E12000004",
    "F": "E12000005",
    "G": "E12000006",
    "H": "E12000007",
    "J": "E12000008",
    "K": "E12000009",
}


class Command(CSVScraper):
    name = 'schools_gias'
    allowed_domains = ['service.gov.uk', 'ea-edubase-api-prod.azurewebsites.net']
    start_urls = [
        "https://get-information-schools.service.gov.uk/Downloads",
    ]
    org_id_prefix = "GB-EDU"
    id_field = "URN"
    source = {
        "title": "Get information about schools",
        "description": "",
        "identifier": "gias",
        "license": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Department for Education",
            "website": "https://www.gov.uk/government/organisations/department-for-education",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "",
                "title": "Establishment fields CSV"
            }
        ],
    }

    date_format = "%d-%m-%Y"
    gias_regex = re.compile(r"https?://ea-edubase-api-prod.azurewebsites.net/edubase/downloads/public/edubasealldata[0-9]{8}\.csv")
    date_fields = ["OpenDate", "CloseDate"]
    location_fields = ["GOR", "DistrictAdministrative", "AdministrativeWard",
                       "ParliamentaryConstituency", "UrbanRural", "MSOA", "LSOA"]
    orgtypes = ['Education']

    def set_session(self, install_cache=False):
        if install_cache:
            self.logger.info("Using requests_cache")
            requests_cache.install_cache('http_cache')
        self.session = HTMLSession()

    def fetch_file(self):
        self.files = {}
        for u in self.start_urls:
            response = self.session.get(u)
            for link in response.html.links:
                if self.gias_regex.match(link):
                    self.files[link] = self.session.get(link)

    def depluralise(self, s):
        if not isinstance(s, str):
            return s
        if s == 'Other types':
            return "Other school"
        if s.endswith("ies"):
            return s[:-3] + "y"
        if s.endswith("s"):
            return s[:-1]
        return s

    def parse_row(self, record):

        record = self.clean_fields(record)

        org_types = [
            self.orgtype_cache["education"],
            self.add_org_type(self.depluralise(
                record.get("EstablishmentTypeGroup (name)"))),
            self.add_org_type(self.depluralise(
                record.get("TypeOfEstablishment (name)"))),
        ]

        self.records.append(
            Organisation(
                org_id=self.get_org_id(record),
                name=record.get("EstablishmentName"),
                charityNumber=None,
                companyNumber=None,
                streetAddress=record.get("Street"),
                addressLocality=record.get("Locality"),
                addressRegion=record.get("Address3"),
                addressCountry=record.get("Country (name)"),
                postalCode=self.parse_postcode(record.get("Postcode")),
                telephone=record.get("TelephoneNum"),
                alternateName=[],
                email=None,
                description=None,
                organisationType=[o.slug for o in org_types],
                organisationTypePrimary=org_types[1],
                url=self.parse_url(record.get("SchoolWebsite")),
                location=self.get_locations(record),
                latestIncome=None,
                dateModified=datetime.datetime.now(),
                dateRegistered=record.get("OpenDate"),
                dateRemoved=record.get("CloseDate"),
                active=record.get("EstablishmentStatus (name)") != "Closed",
                parent=record.get("PropsName"),
                orgIDs=self.get_org_ids(record),
                scrape=self.scrape,
                source=self.source,
                spider=self.name,
                org_id_scheme=self.orgid_scheme,
            )
        )

    def get_org_ids(self, record):
        org_ids = [self.get_org_id(record)]
        if record.get("UKPRN"):
            org_ids.append("GB-UKPRN-{}".format(record.get("UKPRN")))
        if record.get("EstablishmentNumber") and record.get("LA (code)"):
            org_ids.append("GB-LAESTAB-{}/{}".format(
                record.get("LA (code)").rjust(3, "0"),
                record.get("EstablishmentNumber").rjust(4, "0"),
            ))

        return org_ids

    def get_locations(self, record):
        locations = []
        for f in self.location_fields:
            code = record.get(f + " (code)", "")
            name = record.get(f + " (name)", "")

            if name == "" and code == "":
                continue

            if f == "GOR":
                code = REGION_CONVERT.get(code, code)

            if code == "":
                code = name

            locations.append({
                "id": code,
                "name": record.get(f + " (name)"),
                "geoCode": code,
                "geoCodeType": AREA_TYPES.get(code[0:3], f),
            })

        return locations
