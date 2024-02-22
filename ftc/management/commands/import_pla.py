import datetime

from ftc.management.commands._la_locations import LA_LOCATIONS
from ftc.management.commands.import_lae import Command as LAECommand
from ftc.models import Organisation, OrganisationLocation


class Command(LAECommand):
    name = "pla"
    allowed_domains = ["register.gov.uk"]
    start_urls = [
        "https://raw.githubusercontent.com/drkane/registers-backup/main/principal-local-authority.csv"
    ]
    org_id_prefix = "GB-PLA"
    id_field = "key"
    date_fields = ["entry-timestamp", "start-date", "end-date"]
    date_format = {
        "entry-timestamp": "%Y-%m-%dT%H:%M:%SZ",
        "start-date": "%Y-%m-%d",
        "end-date": "%Y-%m-%d",
    }
    source = {
        "title": "Principal local authorities in Wales register",
        "description": "Principal local authorities in Wales",
        "identifier": "pla",
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
                "accessURL": "https://www.registers.service.gov.uk/registers/principal-local-authority/",
                "title": "Principal local authorities in Wales register",
            }
        ],
    }
    orgtypes = [
        "Local Authority",
        "Principal Local Authority (Wales)",
    ]

    def parse_row(self, record):
        record = self.clean_fields(record)
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
                    "addressCountry": "Wales",
                    "postalCode": None,
                    "telephone": None,
                    "alternateName": self.get_alternate_names(
                        record.get("official-name")
                    ),
                    "email": None,
                    "description": None,
                    "organisationType": list(self.orgtype_cache.keys()),
                    "organisationTypePrimary": self.orgtype_cache["local-authority"],
                    "url": None,
                    # "location": locations,
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
