import datetime
import io
import json
import zipfile

from ftc.management.commands._base_scraper import BaseScraper
from ftc.models import Organisation

ROR_PREFIX = "https://ror.org/"


class Command(BaseScraper):
    name = "ror"
    allowed_domains = ["zenodo.org"]
    start_urls = [
        "https://zenodo.org/api/records/?communities=ror-data&sort=mostrecent"
    ]
    org_id_prefix = "XI-ROR"
    id_field = "id"
    source = {
        "title": "Research Organization Registry",
        "description": """ROR (Research Organization Registry) is a community-led registry of open, sustainable, usable, and unique identifiers for every research organization in the world.

ROR includes identifiers and metadata for more than 100,000 organizations. ROR identifiers are designed to link research organizations to research outputs in scholarly infrastructure. Search the ROR registry at https://ror.org/search.""",
        "identifier": "ror",
        "license": "https://creativecommons.org/publicdomain/zero/1.0/",
        "license_name": "Creative Commons Public Domain 1.0 International licence",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Research Organization Registry Community",
            "website": "https://ror.org/",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "https://ror.readme.io/docs/data-dump",
                "title": "ROR Data Dump",
            }
        ],
    }
    included_countries = ["GB"]

    def get_org_id(self, record):
        return "-".join(
            [self.org_id_prefix, str(record.get(self.id_field)).replace(ROR_PREFIX, "")]
        )

    def parse_file(self, response, source_url):
        zip_link = (
            response.json()
            .get("hits", {})
            .get("hits", [])[0]
            .get("files", [])[-1]
            .get("links", {})
            .get("self")
        )
        self.logger.info("Fetching zip: {}".format(zip_link))

        response = self.session.get(zip_link)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            for name in z.namelist():
                if not name.endswith(".json") or name.startswith("__MACOSX"):
                    continue
                self.logger.info("Opening: {}".format(name))
                with z.open(name) as json_data:
                    data = json.load(json_data, encoding="utf-8")
                    rowcount = 0
                    for k, i in enumerate(data):

                        # We only want data from certain countries
                        if (
                            i.get("country", {}).get("country_code")
                            not in self.included_countries
                        ):
                            continue

                        # And we only want certain types of organisation (eg exclude private companies)
                        if "Company" in i.get("types", []):
                            continue

                        rowcount += 1

                        self.parse_row(i)

    def parse_row(self, record):

        record = self.clean_fields(record)

        address = []
        for a in ["line_1", "line_2", "line_3"]:
            an = record.get("addresses", [{}])[0].get(a)
            if an and an != "":
                address.append(an)

        postcode = record.get("addresses", [{}])[0].get("postcode")
        if not postcode or postcode == "":
            postcode = None

        url = record.get("links")[0] if record.get("links") else None

        parent = None
        for r in record.get("relationships", [{}]):
            if r.get("type") == "Parent":
                parent = self.org_id_prefix + "-" + r.get("id").replace(ROR_PREFIX, "")

        orgtype = record.get("types", [])[0] if record.get("types", []) else "Education"
        orgtypes = []
        if orgtype.lower() == "healthcare":
            orgtypes.append(self.add_org_type("Health organisation"))
        if orgtype.lower() == "facility":
            orgtypes.append(self.add_org_type("Research Facility"))
        elif orgtype.lower() == "government":
            orgtypes.append(self.add_org_type("Government Organisation"))
        elif orgtype.lower() == "university" or record.get("external_ids", {}).get(
            "HESA"
        ):
            orgtypes.append(self.add_org_type("higher-education-institution"))
        else:
            orgtypes.append(self.add_org_type(orgtype + " Institution"))

        self.add_org_record(
            Organisation(
                **{
                    "org_id": self.get_org_id(record),
                    "name": record.get("name"),
                    "charityNumber": None,
                    "companyNumber": None,
                    "streetAddress": ", ".join(address),
                    "addressLocality": record.get("addresses", [{}])[0].get("city"),
                    "addressRegion": record.get("addresses", [{}])[0].get("state"),
                    "addressCountry": record.get("addresses", [{}])[0].get("country"),
                    "postalCode": postcode,
                    "telephone": None,
                    "alternateName": record.get("aliases", [])
                    + record.get("acronyms", []),
                    "email": record.get("email_address"),
                    "description": None,
                    "organisationType": [o.slug for o in orgtypes],
                    "organisationTypePrimary": orgtypes[0],
                    "url": url,
                    "latestIncome": None,
                    "dateModified": datetime.datetime.now(),
                    "dateRegistered": None,
                    "dateRemoved": None,
                    "active": record.get("status") == "active",
                    "parent": parent,
                    "orgIDs": [self.get_org_id(record)]
                    + self.get_org_ids(record.get("external_ids", {})),
                    "scrape": self.scrape,
                    "source": self.source,
                    "spider": self.name,
                    "org_id_scheme": self.orgid_scheme,
                }
            )
        )

    def get_org_ids(self, record):
        orgids = []

        for scheme, value in record.items():
            names = value["all"] if isinstance(value["all"], list) else [value["all"]]
            if scheme == "UKPRN":
                orgids.extend(["GB-UKPRN-{}".format(v) for v in names])
            elif scheme == "HESA":
                orgids.extend(["GB-HESA-{}".format(v) for v in names])
            elif scheme == "UCAS":
                orgids.extend(["GB-UCAS-{}".format(v) for v in names])
            elif scheme == "GRID":
                orgids.extend(["XI-GRID-{}".format(v) for v in names])
            elif scheme == "Wikidata":
                orgids.extend(["XI-WIKIDATA-{}".format(v) for v in names])

        return orgids
