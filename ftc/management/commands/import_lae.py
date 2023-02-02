import datetime

from ftc.management.commands._base_scraper import CSVScraper
from ftc.management.commands._la_locations import LA_LOCATIONS
from ftc.models import Organisation, OrganisationLocation


class Command(CSVScraper):
    name = "lae"
    allowed_domains = ["register.gov.uk"]
    start_urls = [
        "https://raw.githubusercontent.com/drkane/registers-backup/main/local-authority-eng.csv"
    ]
    org_id_prefix = "GB-LAE"
    id_field = "key"
    date_fields = ["entry-timestamp", "start-date", "end-date"]
    date_format = {
        "entry-timestamp": "%Y-%m-%dT%H:%M:%SZ",
        "start-date": "%Y-%m-%d",
        "end-date": "%Y-%m-%d",
    }
    source = {
        "title": "Local authorities in England register",
        "description": "Local authorities in England",
        "identifier": "lae",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Ministry of Housing, Communities and Local Government",
            "website": "https://www.gov.uk/government/organisations/ministry-of-housing-communities-and-local-government",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "https://www.registers.service.gov.uk/registers/local-authority-eng/",
                "title": "Local authorities in England register",
            }
        ],
    }
    orgtypes = ["Local Authority"]

    def parse_row(self, record):
        record = self.clean_fields(record)
        org_types = [
            self.orgtype_cache["local-authority"],
        ]

        if record.get("local-authority-type"):
            org_types.append(
                self.add_org_type(
                    LA_TYPES.get(
                        record.get("local-authority-type"),
                        record.get("local-authority-type"),
                    )
                )
            )
        org_ids = [self.get_org_id(record)]

        gss = LA_LOCATIONS.get(record.get(self.id_field))
        if gss:
            self.add_location_record(
                {
                    "org_id": self.get_org_id(record),
                    "name": record.get("name"),
                    "geoCode": gss,
                    "geoCodeType": OrganisationLocation.GeoCodeTypes.ONS_CODE,
                    "locationType": OrganisationLocation.LocationTypes.AREA_OF_OPERATION,
                    "spider": self.name,
                    "scrape": self.scrape,
                    "source": self.source,
                }
            )

        self.add_org_record(
            Organisation(
                **{
                    "org_id": self.get_org_id(record),
                    "name": record.get("official-name"),
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
                    "description": None,
                    "organisationType": [o.slug for o in org_types],
                    "organisationTypePrimary": org_types[0],
                    "url": None,
                    # "locations": locations,
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
                    "org_id_scheme": self.orgid_scheme,
                }
            )
        )


LA_TYPES = {
    "BGH": "Borough",
    "CIT": "City",
    "CC": "City corporation",
    "CA": "Council area",
    "CTY": "County",
    "DIS": "District",
    "LBO": "London borough",
    "MD": "Metropolitan district",
    "NMD": "Non-metropolitan district",
    "SRA": "Strategic Regional Authority",
    "UA": "Unitary authority",
    "COMB": "Combined authority",
}
