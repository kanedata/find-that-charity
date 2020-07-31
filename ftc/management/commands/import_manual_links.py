import csv
import io

from ftc.management.commands._base_scraper import CSVScraper
from ftc.models import OrganisationLink, Source


# Look up manual links held in charity-lookups repository
class Command(CSVScraper):
    name = "manual_links"
    allowed_domains = ["raw.githubusercontent.com"]

    sources = [
        {
            "title": "University Charity Numbers",
            "description": "",
            "identifier": "university_charity_numbers",
            "license": "",
            "license_name": "",
            "issued": "",
            "modified": "",
            "publisher": {
                "name": "Find that Charity",
                "website": "https://github.com/drkane/charity-lookups",
            },
            "distribution": [
                {
                    "downloadURL": "https://raw.githubusercontent.com/drkane/charity-lookups/master/university-charity-number.csv",
                    "accessURL": "https://github.com/drkane/charity-lookups/blob/master/university-charity-number.csv",
                    "title": "University Charity Numbers",
                }
            ],
            "_parse_row": lambda row: {
                "org_id_a": "GB-HESA-{}".format(row["HESA ID"]),
                "org_id_b": row["OrgID"],
            },
        },
        {
            "title": "Dual Registered UK Charities",
            "description": "A list of charities registered in both England & Wales and Scotland",
            "identifier": "dual_registered",
            "license": "",
            "license_name": "",
            "issued": "",
            "modified": "",
            "publisher": {
                "name": "Find that Charity",
                "website": "https://github.com/drkane/charity-lookups",
            },
            "distribution": [
                {
                    "downloadURL": "https://raw.githubusercontent.com/drkane/charity-lookups/master/dual-registered-uk-charities.csv",
                    "accessURL": "https://github.com/drkane/charity-lookups/blob/master/dual-registered-uk-charities.csv",
                    "title": "Dual Registered UK Charities",
                }
            ],
            "_parse_row": lambda row: {
                "org_id_a": "GB-SC-{}".format(row["Scottish Charity Number"].strip()),
                "org_id_b": "GB-CHC-{}".format(row["E&W Charity Number"].strip()),
            },
        },
        {
            "title": "Charity Reregistrations",
            "description": "A list of charities registered in England & Wales that have been re-registered under a new charity number",
            "identifier": "reregistrations",
            "license": "",
            "license_name": "",
            "issued": "",
            "modified": "",
            "publisher": {
                "name": "Find that Charity",
                "website": "https://github.com/drkane/charity-lookups",
            },
            "distribution": [
                {
                    "downloadURL": "https://raw.githubusercontent.com/drkane/charity-lookups/master/charity-reregistrations.csv",
                    "accessURL": "https://github.com/drkane/charity-lookups/blob/master/charity-reregistrations.csv",
                    "title": "Charity Reregistrations",
                }
            ],
            "_parse_row": lambda row: {
                "org_id_a": "GB-CHC-{}".format(row["Old charity number"].strip()),
                "org_id_b": "GB-CHC-{}".format(row["New charity number"].strip()),
            },
        },
        {
            "title": "Registered housing providers",
            "description": "A list of charity numbers and company numbers found for registered housing providers",
            "identifier": "rsp_charity_company",
            "license": "",
            "license_name": "",
            "issued": "",
            "modified": "",
            "publisher": {
                "name": "Find that Charity",
                "website": "https://github.com/drkane/charity-lookups",
            },
            "distribution": [
                {
                    "downloadURL": "https://raw.githubusercontent.com/drkane/charity-lookups/master/rsp-charity-number.csv",
                    "accessURL": "https://github.com/drkane/charity-lookups/blob/master/rsp-charity-number.csv",
                    "title": "Registered housing providers",
                }
            ],
            "_parse_csv": "rsp_charity_company_csv",
            "_encoding": "utf-16",
        },
        {
            "title": "University Royal Charters",
            "description": "A list of royal charter company numbers for universities",
            "identifier": "university_royal_charters",
            "license": "",
            "license_name": "",
            "issued": "",
            "modified": "",
            "publisher": {
                "name": "Find that Charity",
                "website": "https://github.com/drkane/charity-lookups",
            },
            "distribution": [
                {
                    "downloadURL": "https://raw.githubusercontent.com/drkane/charity-lookups/master/university-royal-charters.csv",
                    "accessURL": "https://github.com/drkane/charity-lookups/blob/master/university-royal-charters.csv",
                    "title": "University Royal Charters",
                }
            ],
            "_parse_row": lambda row: {
                "org_id_a": "GB-EDU-{}".format(row["URN"].strip()),
                "org_id_b": "GB-COH-{}".format(row["CompanyNumber"].strip()),
            },
        },
        {
            "title": "Independent Schools Charity Numbers",
            "description": "A list of charity numbers for independent schools",
            "identifier": "independent_schools_ew",
            "license": "",
            "license_name": "",
            "issued": "",
            "modified": "",
            "publisher": {
                "name": "Find that Charity",
                "website": "https://github.com/drkane/charity-lookups",
            },
            "distribution": [
                {
                    "downloadURL": "https://raw.githubusercontent.com/drkane/charity-lookups/master/independent-schools-ew.csv",
                    "accessURL": "https://github.com/drkane/charity-lookups/blob/master/independent-schools-ew.csv",
                    "title": "Independent Schools Charity Numbers",
                }
            ],
            "_parse_row": lambda row: {
                "org_id_a": "GB-EDU-{}".format(row["URN"].strip()),
                "org_id_b": "GB-CHC-{}".format(row["charity_number"].strip())
                if row["charity_number"].strip()
                else None,
            },
        },
        {
            "title": "Register of Mergers",
            "description": "Register of Mergers kept by the Charity Commission for England and Wales.",
            "identifier": "rom",
            "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/",
            "license_name": "Open Government Licence v2.0",
            "issued": "",
            "modified": "",
            "publisher": {
                "name": "Charity Commission for England and Wales",
                "website": "https://www.gov.uk/charity-commission",
            },
            "distribution": [
                {
                    "downloadURL": "https://raw.githubusercontent.com/drkane/charity-lookups/master/ccew-register-of-mergers.csv",
                    "accessURL": "https://github.com/drkane/charity-lookups/blob/master/ccew-register-of-mergers.csv",
                    "title": "Register of Mergers",
                }
            ],
            "_parse_row": lambda row: {
                "org_id_a": "GB-CHC-{}".format(row["transferor_regno"].strip())
                if row["transferor_subno"].strip() == "0"
                else None,
                "org_id_b": "GB-CHC-{}".format(row["transferee_regno"].strip())
                if row["transferee_subno"].strip() == "0"
                else None,
                "description": "merger",
            },
        },
        {
            "title": "CIO Company Numbers",
            "description": "Match between CIO company numbers held by Companies House and their charity number",
            "identifier": "cio_company_numbers",
            "license": "",
            "license_name": "",
            "issued": "",
            "modified": "",
            "publisher": {
                "name": "Find that Charity",
                "website": "https://github.com/drkane/charity-lookups",
            },
            "distribution": [
                {
                    "downloadURL": "https://raw.githubusercontent.com/drkane/charity-lookups/master/cio_company_numbers.csv",
                    "accessURL": "https://github.com/drkane/charity-lookups/blob/master/cio_company_numbers.csv",
                    "title": "CIO Company Numbers",
                }
            ],
            "_parse_row": lambda row: {
                "org_id_a": "GB-COH-{}".format(row["company_number"].strip())
                if row["company_number"].strip()
                else None,
                "org_id_b": "GB-CHC-{}".format(row["charity_number"].strip())
                if row["charity_number"].strip()
                else None,
            },
        },
    ]

    def fetch_file(self):
        self.files = {}
        self.source_cache = {}
        for s in self.sources:
            self.source_cache[s["identifier"]], _ = Source.objects.get_or_create(
                id=s["identifier"],
                defaults={
                    "data": {k: v for k, v in s.items() if not k.startswith("_")}
                },
            )
            r = self.session.get(s["distribution"][0]["downloadURL"])
            r.encoding = s.get("_encoding", "utf8")
            self.files[s["identifier"]] = r

    def parse_file(self, response, source):

        source = [s for s in self.sources if s["identifier"] == source][0]

        if source.get("_parse_csv"):
            return getattr(self, source.get("_parse_csv"))(response, source)

        with io.StringIO(response.text) as a:
            csvreader = csv.DictReader(a)
            for row in csvreader:
                if "_parse_row" in source:
                    row = source["_parse_row"](row)
                row["source"] = source["identifier"]
                if row.get("org_id_a") and row.get("org_id_b"):
                    self.link_records.append(
                        OrganisationLink(
                            org_id_a=row["org_id_a"],
                            org_id_b=row["org_id_b"],
                            spider=self.name,
                            source=self.source_cache[source["identifier"]],
                            scrape=self.scrape,
                        )
                    )
                    self.object_count += 1

    def rsp_charity_company_csv(self, response, source):

        with io.StringIO(response.text) as a:
            csvreader = csv.DictReader(a)
            for row in csvreader:
                if row["Charity Number"].strip() != "":
                    self.link_records.append(
                        OrganisationLink(
                            org_id_a="GB-SHPE-{}".format(row["RP Code"].strip()),
                            org_id_b="GB-CHC-{}".format(row["Charity Number"].strip()),
                            spider=self.name,
                            source=self.source_cache[source["identifier"]],
                            scrape=self.scrape,
                        )
                    )
                    self.object_count += 1
                if row["Company Number"].strip() != "":
                    self.link_records.append(
                        OrganisationLink(
                            org_id_a="GB-SHPE-{}".format(row["RP Code"].strip()),
                            org_id_b="GB-COH-{}".format(row["Company Number"].strip()),
                            spider=self.name,
                            source=self.source_cache[source["identifier"]],
                            scrape=self.scrape,
                        )
                    )
                    self.object_count += 1
