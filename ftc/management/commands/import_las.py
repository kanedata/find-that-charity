import datetime

from ftc.management.commands._la_locations import LA_LOCATIONS
from ftc.management.commands.import_lae import LA_TYPES
from ftc.management.commands.import_lae import Command as LAECommand
from ftc.models import Organisation, OrganisationLocation


class Command(LAECommand):
    name = "las"
    allowed_domains = ["register.gov.uk"]
    start_urls = [
        "https://raw.githubusercontent.com/drkane/registers-backup/main/local-authority-sct.csv"
    ]
    org_id_prefix = "GB-LAS"
    id_field = "key"
    date_fields = ["entry-timestamp", "start-date", "end-date"]
    date_format = {
        "entry-timestamp": "%Y-%m-%dT%H:%M:%SZ",
        "start-date": "%Y-%m-%d",
        "end-date": "%Y-%m-%d",
    }
    source = {
        "title": "[Archived] Local authorites in Scotland register",
        "description": "Local authorities in Scotland This register was part of GOV.UK registers which was retired in 2021. [More information is available on gov.uk](https://www.data.gov.uk/dataset/a8f488fd-eaea-4176-92b0-6d0437b4d121/historical-gov-uk-registers).",
        "identifier": "las",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Scottish Government",
            "website": "https://gov.scot/",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "https://www.registers.service.gov.uk/registers/local-authority-sct/",
                "title": "Local authorites in Scotland register",
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
                    "addressCountry": "Scotland",
                    "postalCode": None,
                    "telephone": None,
                    "alternateName": self.get_alternate_names(
                        record.get("official-name")
                    ),
                    "email": None,
                    "description": None,
                    "organisationType": [o.slug for o in org_types],
                    "organisationTypePrimary": org_types[0],
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
