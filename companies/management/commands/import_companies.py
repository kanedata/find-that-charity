import csv
import datetime
import io
import re
import zipfile

import requests
import requests_cache
import tqdm
from django.core import management
from requests_html import HTMLSession

from companies.models import Company, CompanyCategoryChoices, PreviousName, SICCode
from ftc.management.commands._base_scraper import CSVScraper
from ftc.models import (
    Organisation,
    OrganisationLink,
    OrganisationLocation,
    Vocabulary,
    VocabularyEntries,
)

from ._company_sql import UPDATE_COMPANIES


class Command(CSVScraper):
    name = "companies"
    allowed_domains = ["companieshouse.gov.uk"]
    start_urls = ["http://download.companieshouse.gov.uk/en_output.html"]
    zip_regex = re.compile(r".*/BasicCompanyData-.*\.zip")
    org_id_prefix = "GB-COH"
    clg_types = [
        CompanyCategoryChoices.CLG_LIMITED,
        CompanyCategoryChoices.CLG,
    ]
    orgtypes = [
        "Registered Company",
        "Company Limited by Guarantee",
        CompanyCategoryChoices.CIO,  # "Charitable Incorporated Organisation"
        CompanyCategoryChoices.CIC,  # "Community Interest Company"
        CompanyCategoryChoices.IPS,  # "Industrial and Provident Society"
        CompanyCategoryChoices.CLG_LIMITED,  # "PRI/LBG/NSC (Private, Limited by guarantee, no share capital, use of 'Limited' exemption)"
        CompanyCategoryChoices.CLG,  # "PRI/LTD BY GUAR/NSC (Private, limited by guarantee, no share capital)"
        CompanyCategoryChoices.RS,  # "Registered Society"
        CompanyCategoryChoices.RC,  # "Royal Charter Company"
        CompanyCategoryChoices.SCIO,  # "Scottish Charitable Incorporated Organisation"
    ]
    id_field = "CompanyNumber"
    date_fields = [
        "DissolutionDate",
        "IncorporationDate",
        "Accounts_NextDueDate",
        "Accounts_LastMadeUpDate",
        "Returns_NextDueDate",
        "Returns_LastMadeUpDate",
        "ConfStmtNextDueDate",
        "ConfStmtLastMadeUpDate",
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
    models_to_delete = [
        Organisation,
        OrganisationLink,
        OrganisationLocation,
        Company,
        SICCode,
        PreviousName,
    ]

    def handle(self, *args, **options):
        self.sic_cache = {}
        self.vocab = Vocabulary.objects.get_or_create(
            title="Companies House SIC Codes", single=False
        )[0]
        self.post_sql = UPDATE_COMPANIES
        super().handle()
        management.call_command("update_orgids")

    def set_session(self, install_cache=False):
        if install_cache:
            self.logger.info("Using requests_cache")
            requests_cache.install_cache("http_cache")
        self.session = HTMLSession()

    def fetch_file(self):
        self.files = {}
        for u in self.start_urls:
            response = self.session.get(u)
            response.raise_for_status()
            for link in response.html.absolute_links:
                if self.zip_regex.match(link):
                    self.logger.info("Fetching: {}".format(link))
                    try:
                        self.files[link] = self.session.get(link)
                        self.files[link].raise_for_status()
                    except requests.exceptions.ChunkedEncodingError as err:
                        self.logger.error("Error fetching: {}".format(link))
                        self.logger.error(str(err))

    def parse_file(self, response, source_url):
        self.logger.info("Opening: {}".format(source_url))
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            for f in z.infolist():
                self.logger.info("Opening: {}".format(f.filename))
                with z.open(f) as csvfile:
                    reader = csv.DictReader(
                        io.TextIOWrapper(csvfile, encoding="latin1")
                    )
                    for row in tqdm.tqdm(reader):
                        self.parse_row(row)
        response = None

    def parse_row(self, row):
        row = {k.strip().replace(".", "_"): row[k] for k in row}
        row = self.clean_fields(row)

        company_category = (
            "Company Limited by Guarantee"
            if row.get("CompanyCategory") in self.clg_types
            else row.get("CompanyCategory")
        )

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
                            row[k], "%d/%m/%Y"
                        ).date()
                        previous_names[pn[1]]["nameno"] = pn[1]
                    else:
                        previous_names[pn[1]][pn[2]] = row[k]

            elif k.startswith("SICCode_"):
                if row[k] and row[k].replace("None Supplied", "") != "":
                    sic_code = row[k].split(" - ", maxsplit=1)
                    sic_codes.append(
                        {"code": sic_code[0].strip(), "name": sic_code[1].strip()}
                    )
                    if sic_code[0].strip() not in self.sic_cache:
                        vocab_entry = VocabularyEntries.objects.get_or_create(
                            vocabulary=self.vocab,
                            code=sic_code[0].strip(),
                            title=sic_code[1].strip(),
                            current=True,
                        )
                        self.sic_cache[sic_code[0].strip()] = vocab_entry
            else:
                record[k] = row[k]

        record["previous_names"] = list(previous_names.values())
        record["sic_codes"] = sic_codes

        address1 = []
        for f in [
            "RegAddress_CareOf",
            "RegAddress_POBox",
            "RegAddress_AddressLine1",
            "RegAddress_AddressLine2",
        ]:
            if record.get(f):
                address1.append(record.get(f))

        orgtypes = [
            self.add_org_type(company_category),
            self.orgtype_cache["registered-company"],
        ]

        self.add_record(
            Company,
            {
                **{
                    k: v
                    for k, v in record.items()
                    if k not in ("sic_codes", "previous_names")
                },
                "org_id": self.get_org_id(record),
                "scrape": self.scrape,
                "spider": self.name,
            },
        )
        for n in record["previous_names"]:
            self.add_record(
                PreviousName,
                {
                    "org_id": self.get_org_id(record),
                    "CompanyName": n["CompanyName"],
                    "ConDate": n["CONDATE"],
                    "scrape": self.scrape,
                    "spider": self.name,
                },
            )
        for s in record["sic_codes"]:
            self.add_record(
                SICCode,
                {
                    "org_id": self.get_org_id(record),
                    "code": s["code"],
                    "scrape": self.scrape,
                    "spider": self.name,
                },
            )

        # We only want data from a subset of companies
        if row.get("CompanyCategory") not in self.orgtypes:
            return

        self.add_org_record(
            Organisation(
                **{
                    "org_id": self.get_org_id(record),
                    "name": record.get("CompanyName"),
                    "charityNumber": None,
                    "companyNumber": record.get(self.id_field),
                    "streetAddress": ", ".join(address1),
                    "addressLocality": record.get("RegAddress_PostTown"),
                    "addressRegion": record.get("RegAddress_County"),
                    "addressCountry": record.get("RegAddress_Country"),
                    "postalCode": record.get("RegAddress_PostCode"),
                    "telephone": None,
                    "alternateName": record["previous_names"],
                    "email": None,
                    "description": None,
                    "organisationType": [o.slug for o in orgtypes],
                    "organisationTypePrimary": orgtypes[0],
                    "url": None,
                    "latestIncome": None,
                    "dateModified": datetime.datetime.now(),
                    "dateRegistered": record.get("IncorporationDate"),
                    "dateRemoved": record.get("DissolutionDate"),
                    "active": (
                        record.get("CompanyStatus")
                        not in ["Dissolved", "Inactive", "Converted / Closed"]
                        and not record.get("DissolutionDate")
                    ),
                    "parent": None,
                    "orgIDs": [self.get_org_id(record)],
                    "scrape": self.scrape,
                    "source": self.source,
                    "spider": self.name,
                    "org_id_scheme": self.orgid_scheme,
                }
            )
        )
