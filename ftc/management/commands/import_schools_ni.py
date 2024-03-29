import csv
import datetime
import io

from ftc.management.commands._base_scraper import HTMLScraper
from ftc.models import Organisation


class Command(HTMLScraper):
    name = "schools_ni"
    allowed_domains = ["education-ni.gov.uk"]
    start_urls = ["http://apps.education-ni.gov.uk/appinstitutes/default.aspx"]
    skip_rows = 5
    org_id_prefix = "GB-IRN"
    id_field = "Institution Reference Number"
    date_fields = ["Date Closed"]
    source = {
        "title": "Department of Education - Institution Search",
        "description": "",
        "identifier": "nideptofeducation",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Northern Ireland Department of Education",
            "website": "https://www.education-ni.gov.uk/",
        },
        "distribution": [
            {"downloadURL": "", "accessURL": "", "title": "Institution Search"}
        ],
    }
    orgtypes = ["Education Institution"]

    def fetch_file(self):
        self.files = {}
        for u in self.start_urls:
            r = self.session.get(u, verify=self.verify_certificate)
            r.raise_for_status()
            self.set_access_url(u)
            self.files[u] = self._get_csv_file(r, u, r.cookies)

    def _get_csv_file(self, response, source_url, cookies=None):
        post_params = {
            "__EVENTARGUMENT": "",
            "__EVENTTARGET": "",
            "__EVENTVALIDATION": "",
            "__VIEWSTATE": "",
            "__VIEWSTATEENCRYPTED": "",
            "__VIEWSTATEGENERATOR": "",
            "as_fid": "",
            "as_sfid": "",
            "ctl00$ContentPlaceHolder1$instAddr$instAddr_hfv": "",
            "ctl00$ContentPlaceHolder1$instCounty": "",
            "ctl00$ContentPlaceHolder1$instMgt": "",
            "ctl00$ContentPlaceHolder1$instName$instName_hfv": "",
            "ctl00$ContentPlaceHolder1$instPhone$instPhone_hfv": "",
            "ctl00$ContentPlaceHolder1$instPostcode$instPostcode_hfv": "",
            "ctl00$ContentPlaceHolder1$instRef$instRef_hfv": "",
            "ctl00$ContentPlaceHolder1$instStatus": "-1",
            "ctl00$ContentPlaceHolder1$instTown": "",
            "ctl00$ContentPlaceHolder1$instType": "-1",
            "ctl00$ContentPlaceHolder1$lvSchools$exportFilename$exportFilename_hfv": "U2Nob29sc19QbHVzXzE3X1NlcF8yMDE4XzExXzQ3",
            "ctl00$ContentPlaceHolder1$lvSchools$exportType": "2",
        }
        for p in post_params:
            el = response.html.find('input[name="{}"]'.format(p), first=True)
            if el:
                post_params[p] = el.attrs.get("value", "")
        post_params["ctl00$ContentPlaceHolder1$instType"] = "-2"
        post_params["ctl00$ContentPlaceHolder1$lvSchools$exportType"] = "2"
        post_params["__EVENTTARGET"] = "ctl00$ContentPlaceHolder1$lvSchools$btnDoExport"
        post_params["__EVENTARGUMENT"] = ""

        r = self.session.post(
            self.start_urls[0],
            data=post_params,
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-GB,en-US;q=0.7,en;q=0.3",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                # "Content-Length": "12677",
                "Content-Type": "application/x-www-form-urlencoded",
                # "Cookie": "ASP.NET_SessionId=wl4k0vncy22g1qqb3lwlq5my; CookiePersist=!+X2EE36OE7ulB+JCSgh2GD+ElYVd8ovUgXUOYcC+E/1pLtPiJ/NKfn8u4FX95gYy8NaGOmePK1nAx8c=; TS01690ce2=017f41f17b77ec278b7df07d7e6fa6192f9f768f3a4139b2bd6444df4b0c5d5e81d49d7c68a22f17141f2469d9bebe105edb30f805310290f2254d408e4595d7bd186b4c31955e3c3dbaf0d5002a97ad65d3e3f384; TSb21aa7bb027=08108c6895ab2000d5cc63184ef81a6c81c2679dd0dc3772f90e833efb2e48d90a1c9128d33c3ed808f2ff98a2113000caf8222c22a66dd680f58cd298e20631b8917e4aca7bdc8d1e1b0627e99b84082a024a5471a1aa3285a91d2cbb0670e6",
                "DNT": "1",
                "Host": "apps.education-ni.gov.uk",
                "Origin": "https://apps.education-ni.gov.uk",
                "Pragma": "no-cache",
                "Referer": "https://apps.education-ni.gov.uk/appinstitutes/default.aspx",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            },
            cookies=cookies,
        )
        r.raise_for_status()
        return r

    def parse_file(self, response, source_url):
        try:
            csv_text = response.text
        except AttributeError:
            csv_text = response.body.decode(self.encoding)

        with io.StringIO(csv_text) as a:
            csvreader = csv.DictReader(a)
            for k, row in enumerate(csvreader):
                self.parse_row(row)

    def parse_row(self, record):
        if record.get(self.id_field) == "UNKNOWN":
            return

        record = self.clean_fields(record)

        address = ", ".join(
            [
                record.get("Address Line {}".format(f))
                for f in [1, 2, 3]
                if record.get("Address Line {}".format(f))
            ]
        )
        org_types = [
            self.orgtype_cache["education-institution"],
            self.add_org_type(record.get("Management") + " School"),
            self.add_org_type(record.get("Type", "") + " School"),
        ]
        if org_types[2].slug == "further-education-school":
            org_types[2] = self.add_org_type("Further Education Provider")
        if org_types[2].slug == "preps-school":
            org_types[2] = self.add_org_type("Prep School")

        self.add_org_record(
            Organisation(
                **{
                    "org_id": self.get_org_id(record),
                    "name": record.get("Institution Name"),
                    "charityNumber": None,
                    "companyNumber": None,
                    "streetAddress": address,
                    "addressLocality": record.get("Town"),
                    "addressRegion": record.get("Count"),
                    "addressCountry": "Northern Ireland",
                    "postalCode": self.parse_postcode(record.get("Postcode")),
                    "telephone": record.get("Telephone"),
                    "alternateName": [],
                    "email": record.get("Email"),
                    "description": None,
                    "organisationType": [o.slug for o in org_types],
                    "organisationTypePrimary": org_types[2],
                    "url": None,
                    "latestIncome": None,
                    "dateModified": datetime.datetime.now(),
                    "dateRegistered": None,
                    "dateRemoved": record.get("Date Closed"),
                    "active": record.get("Status") == "Open",
                    "parent": None,
                    "orgIDs": [
                        self.get_org_id(record),
                        f"GB-NIEDU-{record[self.id_field]}",
                    ],
                    "scrape": self.scrape,
                    "source": self.source,
                    "spider": self.name,
                    "org_id_scheme": self.orgid_scheme,
                }
            )
        )
