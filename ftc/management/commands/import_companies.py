import re
import zipfile
import csv
import io
import datetime

from django.core import management
from requests_html import HTMLSession
import requests
import requests_cache
import tqdm

from ftc.management.commands._base_scraper import CSVScraper
from ftc.models import Organisation


class Command(CSVScraper):
    name = 'companies'
    allowed_domains = ['companieshouse.gov.uk']
    start_urls = ["http://download.companieshouse.gov.uk/en_output.html"]
    zip_regex = re.compile(r".*/BasicCompanyData-.*\.zip")
    org_id_prefix = "GB-COH"
    clg_types = [
        "PRI/LBG/NSC (Private, Limited by guarantee, no share capital, use of 'Limited' exemption)",
        "PRI/LTD BY GUAR/NSC (Private, limited by guarantee, no share capital)",
    ]
    orgtypes = [
        "Registered Company",
        "Charitable Incorporated Organisation",
        "Community Interest Company",
        "Company Limited by Guarantee",
        # "Converted/Closed",
        # "European Public Limited-Liability Company (SE)",
        "Industrial and Provident Society",
        # "Investment Company with Variable Capital",
        # "Investment Company with Variable Capital (Securities)",
        # "Investment Company with Variable Capital(Umbrella)",
        # "Limited Liability Partnership",
        # "Limited Partnership",
        # "Old Public Company",
        # "Other Company Type",
        # "Other company type",
        "PRI/LBG/NSC (Private, Limited by guarantee, no share capital, use of 'Limited' exemption)",
        "PRI/LTD BY GUAR/NSC (Private, limited by guarantee, no share capital)",
        # "PRIV LTD SECT. 30 (Private limited company, section 30 of the Companies Act)",
        # "Private Limited Company",
        # "Private Unlimited",
        # "Private Unlimited Company",
        # "Protected Cell Company",
        # "Public Limited Company",
        "Registered Society",
        "Royal Charter Company",
        "Scottish Charitable Incorporated Organisation",
        # "Scottish Partnership",
    ]
    id_field = "CompanyNumber"
    date_fields = [
        "DissolutionDate", "IncorporationDate", "Accounts_NextDueDate", "Accounts_LastMadeUpDate",
        "Returns_NextDueDate", "Returns_LastMadeUpDate", "ConfStmtNextDueDate", "ConfStmtLastMadeUpDate"
    ]
    date_format = "%d/%m/%Y"
    source = {
        "title": "Free Company Data Product",
        "description": "The Free Company Data Product is a downloadable data snapshot containing \
            basic company data of live companies on the register. This snapshot is provided as \
            ZIP files containing data in CSV format and is split into multiple files for ease of \
            downloading.",
        "identifier": "companies",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Companies House",
            "website": "https://www.gov.uk/government/organisations/companies-house",
        },
        "distribution": [],
    }

    def handle(self, *args, **options):
        super().handle()
        management.call_command("update_orgids")

    def fetch_file(self):
        requests_cache.install_cache('http_cache')
        self.session = HTMLSession()
        self.files = {}
        for u in self.start_urls:
            response = self.session.get(u)
            for l in response.html.absolute_links:
                if self.zip_regex.match(l):
                    self.logger.info("Fetching: {}".format(l))
                    try:
                        self.files[l] = self.session.get(l)
                    except requests.exceptions.ChunkedEncodingError as err:
                        self.logger.error("Error fetching: {}".format(l))
                        self.logger.error(str(err))

    def parse_file(self, response, source_url):
        self.logger.info("Opening: {}".format(source_url))
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            for f in z.infolist():
                self.logger.info("Opening: {}".format(f.filename))
                with z.open(f) as csvfile:
                    reader = csv.DictReader(
                        io.TextIOWrapper(csvfile, encoding='latin1'))
                    rowcount = 0
                    for row in tqdm.tqdm(reader):
                        # We only want data from a subset of companies
                        if row.get("CompanyCategory") not in self.orgtypes:
                            continue
                        self.parse_row(row)
        response = None

    def parse_row(self, row):
        row = {k.strip().replace(".", "_"): row[k] for k in row}
        row = self.clean_fields(row)

        if row.get("CompanyCategory") in self.clg_types:
            row["CompanyCategory"] = "Company Limited by Guarantee"

        previous_names = {}
        sic_codes = []
        record = {}
        for k in row:
            if k.startswith("PreviousName_"):
                pn = k.split("_")
                if row[k] and row[k] != "":
                    if pn[1] not in previous_names:
                        previous_names[pn[1]] = {}

                    if pn[2] == "CONDATE":
                        previous_names[pn[1]][pn[2]] = datetime.datetime.strptime(
                            row[k], "%d/%m/%Y").date()
                        previous_names[pn[1]]["nameno"] = pn[1]
                    else:
                        previous_names[pn[1]][pn[2]] = row[k]

            elif k.startswith("SICCode_"):
                if row[k] and row[k].replace("None Supplied", "") != "":
                    sic_code = row[k].split(" - ", maxsplit=1)
                    sic_codes.append({
                        "code": sic_code[0].strip(),
                        "name": sic_code[1].strip()
                    })
            else:
                record[k] = row[k]

        record["previous_names"] = list(previous_names.values())
        record["sic_codes"] = sic_codes

        address1 = []
        for f in ["RegAddress_CareOf", "RegAddress_POBox", "RegAddress_AddressLine1", "RegAddress_AddressLine2"]:
            if record.get(f):
                address1.append(record.get(f))

        orgtypes = [
            self.orgtype_cache['registered-company'],
            self.add_org_type(record.get("CompanyCategory")),
        ]

        self.add_org_record(
            Organisation(**{
                "org_id": self.get_org_id(record),
                "name": self.parse_name(record.get("CompanyName")),
                "charityNumber": None,
                "companyNumber": record.get(self.id_field),
                "streetAddress": ", ".join(address1),
                "addressLocality": record.get("RegAddress_PostTown"),
                "addressRegion": record.get("RegAddress_County"),
                "addressCountry": record.get("RegAddress_Country"),
                "postalCode": record.get("RegAddress_PostCode"),
                "telephone": None,
                "alternateName": [self.parse_name(n["CompanyName"]) for n in record["previous_names"]],
                "email": None,
                "description": None,
                "organisationType": [o.slug for o in orgtypes],
                "organisationTypePrimary": self.add_org_type(record.get("CompanyCategory")),
                "url": None,
                "location": [],
                "latestIncome": None,
                "dateModified": datetime.datetime.now(),
                "dateRegistered": record.get("IncorporationDate"),
                "dateRemoved": record.get("DissolutionDate"),
                "active": (record.get("CompanyStatus") not in ['Dissolved', 'Inactive', 'Converted / Closed'] and not record.get("DissolutionDate")),
                "parent": None,
                "orgIDs": [self.get_org_id(record)],
                "scrape": self.scrape,
                "source": self.source,
                "spider": self.name,
                "org_id_scheme": self.orgid_scheme,
            })
        )
