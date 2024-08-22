import datetime

from ftc.management.commands._base_scraper import HTMLScraper
from ftc.models import Organisation


class Command(HTMLScraper):
    """
    Spider for scraping details of Registered Social Landlords in England
    """

    name = "rsl"
    allowed_domains = ["gov.uk", "githubusercontent.com"]
    start_urls = [
        "https://www.gov.uk/government/publications/current-registered-providers-of-social-housing",
    ]
    org_id_prefix = "GB-SHPE"
    id_field = "registration number"
    source = {
        "title": "Current registered providers of social housing",
        "description": (
            "Current registered providers of social housing and "
            "new registrations and deregistrations. Covers England"
        ),
        "identifier": "rsl",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Regulator of Social Housing",
            "website": "https://www.gov.uk/government/organisations/regulator-of-social-housing",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "",
                "title": "Current registered providers of social housing",
            }
        ],
    }
    orgtypes = ["Registered Provider of Social Housing"]
    date_fields = ["registration date"]
    date_format = "%d/%m/%Y"

    def parse_file(self, response, source_url):
        for link in response.html.absolute_links:
            if "registered-providers-of-social-housing" not in link:
                continue
            r = self.session.get(link)
            r.raise_for_status()

            table = r.html.find("table", first=True)
            if not table:
                self.logger.warning("No table found in {}".format(link))
                continue

            self.set_download_url(link)

            headers = [
                c.text.lower() for c in table.find("thead", first=True).find("th")
            ]
            for k, row in enumerate(table.find("tbody", first=True).find("tr")):
                record = dict(zip(headers, [c.text for c in row.find("td")]))
                self.parse_row(record)

    def parse_row(self, record):
        record = self.clean_fields(record)
        if not record.get("organisation name") or not record.get("registration number"):
            return

        org_types = [
            self.add_org_type("Registered Provider of Social Housing"),
        ]
        if record.get("corporate form"):
            if record["corporate form"].lower() == "Company".lower():
                org_types.append(self.add_org_type("Registered Company"))
                org_types.append(
                    self.add_org_type(
                        "{} {}".format(record["designation"], record["corporate form"])
                    )
                )
            elif (
                record["corporate form"].lower()
                == "CIC-community Interest company".lower()
            ):
                org_types.append(self.add_org_type("Community Interest Company"))
                org_types.append(self.add_org_type("Registered Company"))
            elif (
                record["corporate form"].lower()
                == "LLP-Limited Liability Partnership".lower()
            ):
                org_types.append(self.add_org_type("Limited Liability Partnership"))
                org_types.append(self.add_org_type("Registered Company"))
            elif (
                record["corporate form"].lower()
                == "CIO-Charitable incorporated organisation".lower()
            ):
                org_types.append(
                    self.add_org_type("Charitable Incorporated Organisation")
                )
                org_types.append(self.add_org_type("Registered Charity"))
            elif record["corporate form"].lower() == "Charitable Company".lower():
                org_types.append(self.add_org_type("Registered Company"))
                org_types.append(self.add_org_type("Incorporated Charity"))
                org_types.append(self.add_org_type("Registered Charity"))
            elif record["corporate form"].lower() == "Unincorporated Charity".lower():
                org_types.append(self.add_org_type("Registered Charity"))
            elif record["corporate form"].lower() == "Charity".lower():
                org_types.append(self.add_org_type("Registered Charity"))
            else:
                org_types.append(self.add_org_type(record["corporate form"]))
        elif record.get("designation"):
            org_types.append(self.add_org_type(record["designation"]))

        org_ids = [self.get_org_id(record)]

        self.add_org_record(
            Organisation(
                **{
                    "org_id": self.get_org_id(record),
                    "name": record.get("organisation name"),
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
                    # "location": locations,
                    "latestIncome": None,
                    "dateModified": datetime.datetime.now(),
                    "dateRegistered": record.get("registration date"),
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
