import datetime

from ftc.management.commands._base_scraper import HTMLScraper
from ftc.models import Organisation


class Command(HTMLScraper):
    name = "hesa"
    allowed_domains = ["hesa.ac.uk"]
    start_urls = [
        "https://www.hesa.ac.uk/support/providers",
    ]
    org_id_prefix = "GB-HESA"
    source = {
        "title": "Higher Education Statistics Agency",
        "description": "Higher Education Statistics Agency - we are the experts in UK higher education data and analysis, and the designated data body for England. We collect, process, and publish data about higher education (HE) in the UK. As the trusted source of HE data and analysis, we play a key role in supporting and enhancing the competitive strength of the sector.",
        "identifier": "hesa",
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "license_name": "Creative Commons Attribution 4.0 International Licence",
        "issued": "",
        "modified": "",
        "publisher": {"name": "HESA", "website": "https://www.hesa.ac.uk/",},
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "",
                "title": "HESA - Higher education providers",
            }
        ],
    }
    orgtypes = ["Higher Education"]
    hesa_org_types = {
        "HEI": "University",
        "FEC": "Further Education College",
        "AP": "Alternative Provider",
    }

    def parse_file(self, response, source_url):

        for row in response.html.find("table#heps-table tbody tr"):
            cells = [c.text for c in row.find("td")]

            orgids = [
                "-".join([self.org_id_prefix, str(cells[1])]),
                "-".join(["GB-UKPRN", str(cells[0])]),
            ]

            org_types = [
                self.orgtype_cache["higher-education"],
                self.add_org_type(
                    self.hesa_org_types.get(cells[4].strip(), cells[4].strip())
                ),
            ]

            self.records.append(
                Organisation(
                    **{
                        "org_id": "-".join([self.org_id_prefix, str(cells[1])]),
                        "name": cells[2].strip(),
                        "charityNumber": None,
                        "companyNumber": None,
                        "streetAddress": None,
                        "addressLocality": None,
                        "addressRegion": None,
                        "addressCountry": None,
                        "postalCode": None,
                        "telephone": None,
                        "alternateName": [],
                        "email": None,
                        "description": None,
                        "organisationType": [o.slug for o in org_types],
                        "organisationTypePrimary": org_types[0],
                        "url": None,
                        "location": [],
                        "latestIncome": None,
                        "dateModified": datetime.datetime.now(),
                        "dateRegistered": None,
                        "dateRemoved": None,
                        "active": True,
                        "parent": None,
                        "orgIDs": orgids,
                        "scrape": self.scrape,
                        "source": self.source,
                        "spider": self.name,
                        "org_id_scheme": self.orgid_scheme,
                    }
                )
            )
