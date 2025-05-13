from ftc.management.commands._base_scraper import BaseScraper
from ftc.models import Organisation


class Command(BaseScraper):
    help = "Import gov.uk Organisations Register"
    name = "govuk"
    allowed_domains = ["gov.uk"]
    start_urls = ["https://www.gov.uk/api/organisations"]
    org_id_prefix = "GB-GOVUK"
    id_field = "id"
    date_fields = ["updated_at", "closed_at"]
    source = {
        "title": "Government organisations on GOV.UK",
        "description": "Government departments, agencies or teams that are on the GOV.UK website",
        "identifier": "govuk",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Government Digital Service",
            "website": "https://www.gov.uk/government/organisations/government-digital-service",
        },
        "distribution": [
            {
                "downloadURL": "https://www.gov.uk/api/organisations",
                "accessURL": "https://www.gov.uk/government/organisations",
                "title": "Departments, agencies and public bodies",
            }
        ],
    }
    orgtypes = ["Government Organisation", "Devolved Government"]

    def fetch_file(self):
        self.files = {}
        fetch_url = None
        if hasattr(self, "start_urls"):
            for u in self.start_urls:
                fetch_url = u

        while fetch_url:
            r = self.session.get(fetch_url, verify=self.verify_certificate)
            r.raise_for_status()
            self.files[fetch_url] = r
            fetch_url = r.json().get("next_page_url")

    def parse_file(self, response, source_url):
        self.logger.info("PARSING:" + source_url)
        for result in response.json().get("results", []):
            self.parse_row(result)

    def get_org_id(self, record):
        id_value = str(record.get(self.id_field)).replace(
            "https://www.gov.uk/api/organisations/", ""
        )
        return "-".join([self.org_id_prefix, id_value])

    def parse_row(self, record):
        org_ids = [self.get_org_id(record)]
        if record.get("analytics_identifier"):
            org_ids.append("GB-GOR-" + record.get("analytics_identifier"))

        parent = None
        if record.get("parent_organisations"):
            parent = self.get_org_id(record.get("parent_organisations")[0])

        orgtypes = ["government-organisation"]
        if record["format"] and record["format"] != "Other":
            ot = self.add_org_type(record["format"])
            orgtypes.append(ot.slug)
        if record.get("details", {}).get("govuk_closed_status") == "devolved":
            orgtypes.append("devolved-government")

        devolved_ids = (
            "GB-GOVUK-northern-ireland-executive",
            "GB-GOVUK-welsh-government",
            "GB-GOVUK-the-scottish-government",
        )
        linked_orgs = [
            # self.get_org_id(linked_id)
            # for linked_id in (
            #     record.get("superseded_organisations", [])
            #     + record.get("superseding_organisations", [])
            # )
        ]
        if len(linked_orgs) == 1:
            if linked_orgs[0] not in devolved_ids:
                org_ids.append(linked_orgs[0])

        for linked_id in linked_orgs:
            if linked_id in devolved_ids:
                orgtypes.append("devolved-government")

        alternateNames = []
        if record.get("details", {}).get("abbreviation"):
            alternateNames.append(record.get("details", {}).get("abbreviation"))

        self.add_org_record(
            Organisation(
                **{
                    "org_id": self.get_org_id(record),
                    "name": record.get("title"),
                    "charityNumber": None,
                    "companyNumber": None,
                    "streetAddress": None,
                    "addressLocality": None,
                    "addressRegion": None,
                    "addressCountry": None,
                    "postalCode": None,
                    "telephone": None,
                    "alternateName": alternateNames,
                    "email": None,
                    "description": None,
                    "organisationType": orgtypes,
                    "organisationTypePrimary": self.orgtype_cache[
                        "government-organisation"
                    ],
                    "url": record.get("web_url"),
                    "latestIncome": None,
                    "dateModified": record.get("updated_at"),
                    "dateRegistered": None,
                    "dateRemoved": None,
                    "active": (
                        record.get("details", {}).get("govuk_closed_status")
                        != "no_longer_exists"
                    ),
                    "parent": parent,
                    "orgIDs": org_ids,
                    "scrape": self.scrape,
                    "source": self.source,
                    "spider": self.name,
                    "org_id_scheme": self.orgid_scheme,
                }
            )
        )
