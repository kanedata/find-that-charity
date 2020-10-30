import datetime

from ftc.management.commands._base_scraper import CSVScraper
from ftc.models import Organisation


class Command(CSVScraper):
    name = "mutuals"
    allowed_domains = ["fcastoragemprprod.blob.core.windows.net", "mutuals.fca.org.uk"]
    start_urls = [
        "https://fcastoragemprprod.blob.core.windows.net/societylist/SocietyList.csv",
    ]
    org_id_prefix = "GB-MPR"
    id_field = "Full Registation Number"
    date_fields = ["Registration Date", "Deregistration Date"]
    date_format = "%d/%m/%Y"
    source = {
        "title": "Mutuals Public Register",
        "description": "The Mutuals Public Register is a public record of mutual societies registered by the Financial Conduct Authority. It has information for societies currently registered, and those no longer registered. The types of mutual societies include: Registered societies, including: Co-operative societies; and Community benefit societies, Credit unions, Building societies, Friendly societies",
        "identifier": "mutuals",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Financial Conduct Authority",
            "website": "https://mutuals.fca.org.uk/",
        },
        "distribution": [
            {
                "downloadURL": "https://fcastoragemprprod.blob.core.windows.net/societylist/SocietyList.csv",
                "accessURL": "https://mutuals.fca.org.uk/",
                "title": "Download the Register (CSV of basic society details)"
            }
        ],
    }
    orgtypes = ["Mutual"]

    def parse_row(self, record):

        if not hasattr(self, "org_ids_seen"):
            self.org_ids_seen = []

        record = self.clean_fields(record)

        if self.get_org_id(record) in self.org_ids_seen:
            return
        self.org_ids_seen.append(self.get_org_id(record))

        if not record.get("Society Name"):
            return

        add = record["Society Address"]
        postcode = None
        if isinstance(add, str):
            add = add.strip().split(" ")
            if len(add) > 2:
                if self.postcode_regex.match(" ".join(add[-2:])):
                    postcode = " ".join(add[-2:]).upper()
                    record["Society Address"] = record["Society Address"].replace(postcode, "")
        address, _ = self.split_address(record["Society Address"], get_postcode=False)
        address = dict(enumerate(address))
        org_ids = [self.get_org_id(record)]
        orgtypes = [
            self.orgtype_cache["mutual"],
            self.add_org_type(record.get("Registered As")),
        ]
        description = ""
        if record.get("Registration Act"):
            description = "Registered under {}".format(
                record.get("Registration Act")
            )

        # add org ids for companies
        if record.get("Registered As") in ["Community Benefit Society", "Co-operative Society"]:
            org_ids.append("GB-COH-RS{}".format(record["Full Registation Number"].zfill(6)))

        org_record = {
            "org_id": self.get_org_id(record),
            "name": record.get("Society Name"),
            "charityNumber": None,
            "companyNumber": None,
            "streetAddress": address.get(0),
            "addressLocality": address.get(1),
            "addressRegion": address.get(2),
            "addressCountry": None,
            "postalCode": postcode,
            "telephone": None,
            "alternateName": [],
            "email": None,
            "description": description,
            "organisationType": [o.slug for o in orgtypes],
            "organisationTypePrimary": orgtypes[1],
            "url": None,
            "location": [],
            "latestIncome": None,
            "dateModified": datetime.datetime.now(),
            "dateRegistered": record.get("Registration Date"),
            "dateRemoved": record.get("Deregistration Date"),
            "active": record.get("Society Status", "") != "Deregistered",
            "parent": None,
            "orgIDs": org_ids,
            "scrape": self.scrape,
            "source": self.source,
            "spider": self.name,
            "org_id_scheme": self.orgid_scheme,
        }
        self.records.append(
            Organisation(**org_record)
        )
