import datetime
import re
from collections import defaultdict

from ftc.management.commands._base_scraper import CSVScraper
from ftc.models import Organisation, OrganisationLocation

LA_NAME_REPLACEMENTS = [
    (re.compile(r"\bThe\b"), ""),
    (re.compile(r"\bCity of\b"), ""),
    (re.compile(r"\band\b"), "&"),
    (re.compile(r"\b&\b"), "and"),
    (re.compile(r"\bof Yorkshire\b"), ""),
    (re.compile(r"\bCouncil of the\b"), ""),
    (re.compile(r"^Borough of\b"), ""),
    (re.compile(r"\bBorough Council of\b"), ""),
    (re.compile(r"\bRoyal Borough of\b"), ""),
    (re.compile(r"\bRoyal Borough of\b"), "London Borough of"),
    (re.compile(r"\bLondon Borough of\b"), ""),
    (re.compile(r"\bLondon Borough of\b"), "LB"),
    (re.compile(r"\bComhairle nan\b"), ""),
    (re.compile(r"\bCity and County of \b"), ""),
    (re.compile(r"\b-\b"), " "),
]
LA_SUFFIXES = [
    "Metropolitan Borough Council",
    "Metropolitan District Council",
    "County Borough Council",
    "Borough Council",
    "City Council",
    "City and District Council",
    "County Council",
    "District Council",
    "Islands Council",
    "Council",
    "Mayoral Combined Authority",
    "Combined Authority",
    "Authority",
]


def unique_list_case_insensitive(item_list):
    # return a unique list of items, case insenstive,
    # but keep the original case if there is a conflict
    unique_items = defaultdict(set)
    for item in item_list:
        unique_items[item.lower()].add(item)
    output = []
    for item in unique_items.values():
        cased_versions = [i for i in item if i.lower() != i]
        if cased_versions:
            output.append(cased_versions[0])
        else:
            output.append(item.pop())
    return output


class Command(CSVScraper):
    name = "lamysociety"
    allowed_domains = ["pages.mysociety.org"]
    start_urls = [
        "https://github.com/alphagov/local-links-manager/raw/main/data/local-authorities.csv",
        "https://pages.mysociety.org/uk_local_authority_names_and_codes/data/uk_la_future/latest/uk_local_authorities_future.csv",
    ]
    org_id_prefix = "GB-UKLA"
    id_field = "local-authority-code"
    date_fields = ["start-date", "end-date"]
    date_format = {
        "start-date": "%Y-%m-%d",
        "end-date": "%Y-%m-%d",
    }
    source = {
        "title": "UK Local Authorities",
        "description": "A dataset that includes current and previous local authorities, as well as some planned but not in force yet",
        "identifier": "lamysociety",
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "license_name": "Creative Commons Attribution 4.0 International License",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "MySociety",
            "website": "https://mysociety.org/",
        },
        "distribution": [
            {
                "downloadURL": "https://pages.mysociety.org/uk_local_authority_names_and_codes/downloads/uk-la-future-uk-local-authorities-future-csv/latest",
                "accessURL": "https://pages.mysociety.org/uk_local_authority_names_and_codes/datasets/uk_la_future/latest",
                "title": "UK Local Authorities",
            }
        ],
    }
    orgtypes = ["Local Authority"]

    def get_alternate_names(self, record):
        official_name = record.get("official-name")
        names = [
            official_name,
            record.get("nice-name") + " Council",
        ] + re.split(r",(?![ ])", record.get("alt-names", ""))
        names = [n.strip() for n in names if n.strip()]
        if "City of London Corporation" in names:
            return [
                "City of London Council",
            ]
        alternate_names = names.copy()
        for name_ in names:
            for regex, replacement in LA_NAME_REPLACEMENTS:
                alternate_names.append(regex.sub(replacement, name_).strip())

        for name_ in alternate_names + names:
            for regex, replacement in LA_NAME_REPLACEMENTS:
                alternate_names.append(regex.sub(replacement, name_).strip())

        for suffix in LA_SUFFIXES:
            for name_ in alternate_names + names:
                if name_.endswith(suffix):
                    alternate_names.append(name_.replace(suffix, "Council"))

        for name_ in alternate_names + names:
            if "council" not in name_.lower():
                alternate_names.append(name_ + " Council")

        new_alternate_names = []
        for name in alternate_names:
            if name.lower() not in [n.lower() for n in new_alternate_names]:
                new_alternate_names.append(name)

        not_allowed_names = [
            official_name.lower().strip(),
            "city of",
            "council",
            "city of council",
            "",
        ]

        return [
            n.strip()
            for n in unique_list_case_insensitive(alternate_names)
            if n.lower().strip() not in not_allowed_names
        ]

    def parse_row_gov_uk(self, record):
        # Some rows are from the gov.uk register, and have a different format
        if not hasattr(self, "websites"):
            self.websites = {}

        if record.get("homepage_url"):
            self.websites[record.get("gss")] = record.get("homepage_url")

    def parse_row(self, record):
        record = self.clean_fields(record)

        if "homepage_url" in record:
            return self.parse_row_gov_uk(record)

        org_types = [
            self.orgtype_cache["local-authority"],
        ]

        if record.get("local-authority-type-name"):
            org_types.append(self.add_org_type(record.get("local-authority-type-name")))
        org_ids = [self.get_org_id(record)]
        if record.get("nation") == "England":
            org_ids.append("GB-LAE-{}".format(record.get("local-authority-code")))
        elif record.get("nation") == "Scotland":
            org_ids.append("GB-LAS-{}".format(record.get("local-authority-code")))
        elif record.get("nation") == "Wales":
            org_ids.append("GB-PLA-{}".format(record.get("local-authority-code")))
        elif record.get("nation") == "Northern Ireland":
            org_ids.append("GB-LANI-{}".format(record.get("local-authority-code")))

        gss = record.get("gss-code")
        if gss:
            self.add_location_record(
                {
                    "org_id": self.get_org_id(record),
                    "name": record.get("nice-name"),
                    "geoCode": gss,
                    "geoCodeType": OrganisationLocation.GeoCodeTypes.ONS_CODE,
                    "locationType": OrganisationLocation.LocationTypes.AREA_OF_OPERATION,
                    "spider": self.name,
                    "scrape": self.scrape,
                    "source": self.source,
                }
            )

        website = None
        if hasattr(self, "websites") and record.get("gss-code") in self.websites:
            website = self.websites[record.get("gss-code")]
        elif record.get("gov-uk-slug"):
            website = "https://www.gov.uk/find-local-council/{}".format(
                record.get("gov-uk-slug")
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
                    "addressCountry": record.get("nation"),
                    "postalCode": None,
                    "telephone": None,
                    "alternateName": self.get_alternate_names(record),
                    "email": None,
                    "description": None,
                    "organisationType": [o.slug for o in org_types],
                    "organisationTypePrimary": org_types[0],
                    "url": website,
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
