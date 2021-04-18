import datetime

from ftc.management.commands._base_scraper import CSVScraper
from ftc.models import Organisation


class Command(CSVScraper):
    name = "casc"
    allowed_domains = ["raw.githubusercontent.com"]
    start_urls = [
        "https://raw.githubusercontent.com/ThreeSixtyGiving/cascs/master/casc_company_house.csv",
        "https://raw.githubusercontent.com/ThreeSixtyGiving/cascs/master/cascs.csv",
    ]
    org_id_prefix = "GB-CASC"
    id_field = "id"
    source = {
        "title": "Community amateur sports clubs (CASCs) registered with HMRC",
        "description": "Check which sports clubs are registered with HMRC as community amateur sports clubs. Processed by 360Giving",
        "identifier": "casc",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "HMRC",
            "website": "https://www.gov.uk/government/organisations/hm-revenue-customs",
        },
        "distribution": [
            {
                "downloadURL": "https://github.com/threesixtygiving/cascs",
                "accessURL": "https://www.gov.uk/government/publications/community-amateur-sports-clubs-casc-registered-with-hmrc--2",
                "title": "Government organisations on GOV.UK register",
            }
        ],
    }
    orgtypes = ["Community Amateur Sports Club", "Sports Club", "Registered Company"]

    def parse_row(self, record):

        record = self.clean_fields(record)
        if "casc_orgid" in record.keys():
            if not hasattr(self, "coynos"):
                self.coynos = {}
            self.coynos[record["casc_orgid"]] = record["ch_orgid"]
            return

        address = dict(
            enumerate([v.strip() for v in record["address"].split(",", maxsplit=2)])
        )
        org_ids = [record["id"]]
        orgtypes = [
            self.orgtype_cache["community-amateur-sports-club"],
            self.orgtype_cache["sports-club"],
        ]
        if record["id"] in self.coynos:
            org_ids.append(self.coynos[record["id"]])
            orgtypes.append(self.orgtype_cache["registered-company"])

        self.add_org_record(
            Organisation(
                **{
                    "org_id": record["id"],
                    "name": record["name"],
                    "charityNumber": None,
                    "companyNumber": None,
                    "streetAddress": address.get(0),
                    "addressLocality": address.get(1),
                    "addressRegion": address.get(2),
                    "addressCountry": None,
                    "postalCode": self.parse_postcode(record["postcode"]),
                    "telephone": None,
                    "alternateName": [],
                    "email": None,
                    "description": None,
                    "organisationType": [o.slug for o in orgtypes],
                    "organisationTypePrimary": orgtypes[0],
                    "url": None,
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
