import copy
import csv
import datetime
import io

from ftc.management.commands._base_scraper import HTMLScraper
from ftc.models import Organisation, Source

"""
Import NHS Organisation Data Service (NHS ODS) data.

As of November 2025, the ODS has a new API endpoint for downloading reports, which replaces the previous static ZIP files.

Automate/Schedule the Download of Report Packages

An API endpoint has been created for DSE that enables users to automate / schedule downloads of predefined reports programmatically.

The DSE API endpoint can be queried via an internet browser, API querying tools (i.e. Postman) or via command scripts.

Users can query specific predefined reports or report bundles and optionally filter results to show only records created/amended/closed since a given date or within a specified period of time (i.e. last 7 days).

The response will contain the requested report(s) in an object format or provide error messages when invalid parameters are used.

The report data will be in csv format with no headers, consistent with legacy ODS .csv files previously published on the ODS website or via TRUD. Multiple reports or a report bundle will be output as multiple .csv in a .zip file.

Report specifications are not included in the download, these can be accessed via the ODS Reference Data Catalogue.

Request

Method: GET 
Endpoint: /getReport

Query Parameters
Parameter	Type	Description
report	String	The report name or a comma-separated list of report names for multiple reports. You cannot use this parameter with reportBundle.
reportBundle	String	Use “prescribingDataPack” to get the following reports: 'ebranchs', 'edispensary', 'egmcmem', 'egpcur', 'epcmem', 'epharmacyhq', 'epraccur', 'epracmem'. You cannot use this parameter with report.
lastChangeStart	String 	The start date for filtering reports based on the last changed date. Must be in yyyy-mm-dd format.Used only when querying a single report using the report parameter.
lastChangePeriod	String	A period for filtering reports to include only records added/updated/closed in the period. Must be one of the following: 7, 30, or 90 (e.g., changes in the last 7, 30, or 90 days). Used only when querying multiple reports using the report parameter or querying using reportBundle.

Note:

    When specifying/including report parameters they are case sensitive.
    lastChangeStart only applies when requesting single reports, lastChangePeriod applies only to report bundles/packs.


Response

Success Response (200)

The response body contains an object where each report name is a key, and its corresponding data (in CSV format) is the value.

Example:
{ 
"eauth ": (csvData)
"educate ": (csvData)
}

Error Responses

    400 Bad Request: If any required parameter is missing or invalid, or if conflicting parameters are provided.
    405 Method Not Allowed: If the HTTP method is not GET.

Example:
{ 
"error": "Missing report query parameter"
}

Error Handling

    Missing report or reportBundle query parameter: You must provide either  report or  reportBundle. You cannot use both.
    Invalid date format:  lastChangeStart  must be in yyyy-mm-dd format.
    Invalid use of lastChangeStart: These parameters cannot be used with  reportBundle.
    lastChangePeriod invalid: The value of  lastChangePeriod must be one of 7, 30, or 90.
    Invalid combination of report and lastChangePeriod: If you query a single report, you cannot use lastChangePeriod.
    Future Date Error: Dates cannot be in the future. The API will reject any future dates with a 400 error.


Examples

Get a single report

Request: GET 
https://www.odsdatasearchandexport.nhs.uk/api/getReport?report=eauth

Get report with only changes since a given date

Request: GET 
https://www.odsdatasearchandexport.nhs.uk/api/getReport?report=eauth&lastChangeStart=2025-01-01

Get a premade report bundle (prescribingDataPack) with only changes within a specific period

Request: GET 
https://www.odsdatasearchandexport.nhs.uk/api/getReport?reportBundle=prescribingDataPack&lastChangePeriod=7

Get multiple reports with only changes within a specific period (7, 30 or 90 days)

Request: GET 
https://www.odsdatasearchandexport.nhs.uk/api/getReport?report=eauth,educate&lastChangePeriod=30

Get multiple reports with only changes within a specific period that replicates the amendment files previously provided in the TRUD Weekly Prescribing Data pack

Request: GET 
https://www.odsdatasearchandexport.nhs.uk/api/getReport?report=ebranchs,edispensary,epharmacyhq&lastChangePeriod=7

List of Available Reports

Below is a full list of permitted report names, queries must specify report names in this EXACT format.

Due to their nature (i.e. they may be snapshot files), not all reports are available to run as ‘amendments only’ – these are indicated below.
Permitted Reports (Full Files)	Not available as Amendment Files / 'Changes Since'
eabeydispgp	
eauth	
ebranchs	
ecarehomehq	
ecarehomesite	
eccg	
eccgsite	
econcur	*
ecsu	
ecsusite	
ect	
ectsite	
edconcur	*
edispensary	
educate	
egdpprac	
egmcmem	*
egpcur	
ehospice	
eiom	
ejustice	
enonnhs	
ensa	
enurse	*
eopthq	
eoptsite	
eother	
epcdp	
epcmem	*
epcn	
epcncorepartnerdetails	*
epharmacyhq	
ephp	
ephpsite	
eplab	
epraccur	
epracmem	*
eschools	
espha	
etr	
etreat	
etrust	
ets	
lauth	
lauthsite	
ngpcur	
niorg	
nlhscgpr	*
npraccur	
succ	*
wlhb	
wlhbsite	

Download File Naming Conventions

Zip file naming convention for FULL report bundles/packs

22_04_2025_ prescribingDataPack.zip
22_04_2025_userDefinedPack.zip
Where the date is the date the pack was run/downloaded.

Csv and Zip file naming conventions for AMENDMENTS ONLY report bundles/packs

The first date is the user defined ‘Last Change Date and the ‘to’ date is the date the file was run. i.e.: 

    edispensary_changes_20250301_to_20250424.csv 

or for a bundle, :

    prescribingDataPack_changes_90_days_to_20250424.zip
"""


class Command(HTMLScraper):
    name = "nhsods"
    allowed_domains = ["nhs.uk"]
    start_urls = [
        "https://digital.nhs.uk/services/organisation-data-service/data-search-and-export"
    ]
    org_id_prefix = "GB-NHS"
    id_field = "Code"
    date_fields = ["Open Date", "Close Date", "Join Parent Date", "Left Parent Date"]
    date_format = "%Y%m%d"
    source_template = {
        "title": "NHS Organisation Data Service downloads",
        "description": "",
        "identifier": "nhsods",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {"name": "NHS Digital", "website": "https://digital.nhs.uk/"},
        "distribution": [{"downloadURL": "", "accessURL": "", "title": ""}],
    }
    zipfiles = [
        # {"org_type": "NHS England Commissioning and Government Office Regions", "id": "eauth"},
        {"org_type": "Special Health Authority", "id": "espha"},
        {"org_type": "Commissioning Support Unit", "id": "ecsu"},
        # {"org_type": "Commissioning Support Units sites", "id": "ecsusite"},
        # {"org_type": "Executive Agency Programme", "id": "eother"},
        {"org_type": "NHS Support Agency or Shared Service", "id": "ensa"},
        {"org_type": "GP practice", "id": "epraccur"},
        {"org_type": "Clinical Commissioning Group", "id": "eccg"},
        # {"org_type": "Clinical Commissioning Group sites", "id": "eccgsite"},
        {"org_type": "NHS Trust", "id": "etr"},
        # {"org_type": "NHS Trust sites", "id": "ets"},
        # {"org_type": "NHS Trusts and sites", "id": "etrust"},
        {"org_type": "Care Trust", "id": "ect"},
        # {"org_type": "Care Trust sites", "id": "ectsite"},
        # {"org_type": "Care Trusts and sites", "id": "ecare"},
        {"org_type": "Welsh Local Health Board", "id": "wlhb"},
        # {"org_type": "Welsh Local Health Board sites", "id": "wlhbsite"},
        # {"org_type": "Welsh Local Health Boards and sites", "id": "whbs"},
    ]
    fields = [
        "Code",
        "Name",
        "National Grouping",
        "High Level Health Geography",
        "Address Line 1",
        "Address Line 2",
        "Address Line 3",
        "Address Line 4",
        "Address Line 5",
        "Postcode",
        "Open Date",
        "Close Date",
        "column-13",
        "Organisation Sub-Type Code",
        "Parent Organisation Code",
        "Join Parent Date",
        "Left Parent Date",
        "Contact Telephone Number",
        "column-19",
        "column-20",
        "column-21",
        "Amended record indicator",
        "column-23",
        "column-24",
        "column-25",
        "column-26",
        "column-27",
    ]
    orgtypes = ["Health organisation", "NHS organisation"]

    def fetch_file(self):
        self.files = {}
        self.sources = {}
        for u in self.zipfiles:
            url = "https://www.odsdatasearchandexport.nhs.uk/api/getReport?report={}".format(
                u["id"]
            )
            r = self.session.get(url)
            r.raise_for_status()
            self.files[u["org_type"]] = r

            source = copy.deepcopy(self.source_template)
            source["distribution"] = [
                {
                    "downloadURL": url,
                    "accessURL": self.start_urls[0],
                    "title": u["org_type"],
                }
            ]
            source["title"] = u["org_type"]
            source["modified"] = datetime.datetime.now().isoformat()
            self.sources[u["org_type"]], _ = Source.objects.update_or_create(
                id=f"{source['identifier']}-{u['id']}", defaults={"data": source}
            )

    def parse_file(self, response, org_type):
        content = io.StringIO(response.text)
        reader = csv.DictReader(content, fieldnames=self.fields)
        rowcount = 0
        for row in reader:
            rowcount += 1
            self.parse_row(row, org_type)

    def parse_row(self, record, org_type=None):
        record = self.clean_fields(record)

        org_types = [
            self.orgtype_cache["health-organisation"],
            self.orgtype_cache["nhs-organisation"],
        ]
        if org_type:
            o = self.add_org_type(org_type)
            org_types.append(o)

        address = {
            "streetAddress": record.get("Address Line 1"),
            "addressLocality": record.get("Address Line 3"),
            "addressRegion": record.get("Address Line 5"),
            "addressCountry": None,
        }
        if record.get("Address Line 2"):
            if address["streetAddress"]:
                address["streetAddress"] += ", {}".format(record.get("Address Line 2"))
            else:
                address["streetAddress"] = record.get("Address Line 2")
        if record.get("Address Line 4"):
            if address["addressLocality"]:
                address["addressLocality"] += ", {}".format(
                    record.get("Address Line 4")
                )
            else:
                address["addressLocality"] = record.get("Address Line 4")

        parent = None
        if record.get("Parent Organisation Code"):
            parent = f"{self.org_id_prefix}-{record.get('Parent Organisation Code')}"

        self.add_org_record(
            Organisation(
                **{
                    "org_id": self.get_org_id(record),
                    "name": record.get("Name"),
                    "charityNumber": None,
                    "companyNumber": None,
                    "streetAddress": address["streetAddress"],
                    "addressLocality": address["addressLocality"],
                    "addressRegion": address["addressRegion"],
                    "addressCountry": address["addressCountry"],
                    "postalCode": record.get("Postcode"),
                    "telephone": record.get("Contact Telephone Number"),
                    "alternateName": [],
                    "email": None,
                    "description": None,
                    "organisationType": [o.slug for o in org_types],
                    "organisationTypePrimary": org_types[0],
                    "url": None,
                    "latestIncome": None,
                    "dateModified": datetime.datetime.now(),
                    "dateRegistered": record.get("Open Date"),
                    "dateRemoved": record.get("Close Date"),
                    "active": record.get("Close Date") is None,
                    "parent": parent,
                    "orgIDs": [self.get_org_id(record)],
                    "scrape": self.scrape,
                    "source": self.sources[org_type],
                    "spider": self.name,
                    "org_id_scheme": self.orgid_scheme,
                }
            )
        )
