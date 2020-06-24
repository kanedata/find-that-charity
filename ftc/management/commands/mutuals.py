# # -*- coding: utf-8 -*-
# import datetime
# import io
# import csv

# import scrapy

# from .base_scraper import BaseScraper
# from ..items import Organisation, Source

# class MutualsSpider(BaseScraper):
#     name = 'mutuals'
#     allowed_domains = ['fcastoragemprprod.blob.core.windows.net', 'mutuals.fca.org.uk/']
#     start_urls = [
#         "https://fcastoragemprprod.blob.core.windows.net/societylist/SocietyList.csv"
#     ]
#     org_id_prefix = "GB-MPR"
#     id_field = "Society Number"
#     date_fields = ["Registration Date"]
#     date_format = {
#         "Registration Date": "%d/%m/%Y",
#     }
#     source = {
#         "title": "Mutuals Public Register",
#         "description": "The Mutuals Public Register is a public record of mutual societies registered by the Financial Conduct Authority. It has information for societies currently registered, and those no longer registered. The types of mutual societies include: Registered societies, including: Co-operative societies; and Community benefit societies, Credit unions, Building societies, Friendly societies",
#         "identifier": "mutuals",
#         "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
#         "license_name": "Open Government Licence v3.0",
#         "issued": "",
#         "modified": "",
#         "publisher": {
#             "name": "Financial Conduct Authority",
#             "website": "https://mutuals.fca.org.uk/",
#         },
#         "distribution": [
#             {
#                 "downloadURL": "https://fcastoragemprprod.blob.core.windows.net/societylist/SocietyList.csv",
#                 "accessURL": "https://mutuals.fca.org.uk/",
#                 "title": "Download the Register (CSV of basic society details)"
#             }
#         ],
#     }

#     def start_requests(self):

#         self.source["distribution"][0]["downloadURL"] = self.start_urls[0]
#         self.source["modified"] = datetime.datetime.now().isoformat()

#         return [scrapy.Request(self.start_urls[0], callback=self.parse_csv)]

#     def parse_row(self, record):

#         record = self.clean_fields(record)

#         address, postcode = self.split_address(record.get("Society Address", "").replace(",,,", ""))

#         org_types = [
#             "Mutual Society",
#             record.get("Registered As")
#         ]
#         org_ids = [
#             self.get_org_id(record),
#             "GB-COH-IP{}".format(record.get("Society Number").rjust(6, "0")),
#             "GB-COH-IP{}R".format(record.get("Society Number").rjust(5, "0")),
#         ]

#         return Organisation(**{
#             "id": self.get_org_id(record),
#             "name": record.get("Society Name"),
#             "charityNumber": None,
#             "companyNumber": None,
#             "streetAddress": address[0] if len(address) else None,
#             "addressLocality": address[1] if len(address) > 1 else None,
#             "addressRegion": address[2] if len(address) > 2 else None,
#             "addressCountry": None,
#             "postalCode": postcode,
#             "telephone": None,
#             "alternateName": None,
#             "email": None,
#             "description": record.get("Registration Act"),
#             "organisationType": org_types,
#             "organisationTypePrimary": record.get("Registered As"),
#             "url": None,
#             "location": [],
#             "latestIncome": None,
#             "dateModified": datetime.datetime.now(),
#             "dateRegistered": record.get("Registration Date"),
#             "dateRemoved": None,
#             "active": record.get("Society Status", "").startswith("Registered"),
#             "parent": None,
#             "orgIDs": org_ids,
#             "source": self.source["identifier"],
#         })
