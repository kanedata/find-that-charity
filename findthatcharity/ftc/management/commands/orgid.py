# -*- coding: utf-8 -*-
import scrapy

from ..items import Identifier
from .base_scraper import BaseScraper


class OrgidSpider(BaseScraper):
    name = 'orgid'
    allowed_domains = ['org-id.guide']
    start_urls = ['http://org-id.guide/download.csv']
    bool_fields = [
        "access/availableOnline",
        "confirmed",
        "deprecated",
    ]
    date_fields = ["meta/lastUpdated"]

    def start_requests(self):
        return [scrapy.Request(self.start_urls[0], callback=self.parse_csv)]

    def parse_row(self, row):

        row = self.clean_fields(row)

        item = Identifier()
        item["code"] = row["code"]
        item["description_en"] = row["description/en"]
        item["License"] = row["License"]
        item["access_availableOnline"] = row["access/availableOnline"]
        item["access_exampleIdentifiers"] = row["access/exampleIdentifiers"]
        item["access_guidanceOnLocatingIds"] = row["access/guidanceOnLocatingIds"]
        item["access_languages"] = row["access/languages"]
        item["access_onlineAccessDetails"] = row["access/onlineAccessDetails"]
        item["access_publicDatabase"] = row["access/publicDatabase"]
        item["confirmed"] = row["confirmed"]
        item["coverage"] = row["coverage"]
        item["data_availability"] = row["data/availability"]
        item["data_dataAccessDetails"] = row["data/dataAccessDetails"]
        item["data_features"] = row["data/features"]
        item["data_licenseDetails"] = row["data/licenseDetails"]
        item["data_licenseStatus"] = row["data/licenseStatus"]
        item["deprecated"] = row["deprecated"]
        item["formerPrefixes"] = row["formerPrefixes"]
        item["links_opencorporates"] = row["links/opencorporates"]
        item["links_wikipedia"] = row["links/wikipedia"]
        item["listType"] = row["listType"]
        item["meta_lastUpdated"] = row["meta/lastUpdated"]
        item["meta_source"] = row["meta/source"]
        item["name_en"] = row["name/en"]
        item["name_local"] = row["name/local"]
        item["quality"] = row["quality"]
        item["quality_explained_Availability_API"] = row["quality_explained/Availability: API"]
        item["quality_explained_Availability_BulkDownload"] = row["quality_explained/Availability: Bulk download"]
        item["quality_explained_Availability_CSVFormat"] = row["quality_explained/Availability: CSV format"]
        item["quality_explained_Availability_ExcelFormat"] = row["quality_explained/Availability: Excel format"]
        item["quality_explained_Availability_JSONFormat"] = row["quality_explained/Availability: JSON format"]
        item["quality_explained_Availability_PDFFormat"] = row["quality_explained/Availability: PDF format"]
        item["quality_explained_Availability_RDFFormat"] = row["quality_explained/Availability: RDF format"]
        item["quality_explained_Availability_XMLFormat"] = row["quality_explained/Availability: XML format"]
        item["quality_explained_License_ClosedLicense"] = row["quality_explained/License: Closed License"]
        item["quality_explained_License_NoLicense"] = row["quality_explained/License: No License"]
        item["quality_explained_License_OpenLicense"] = row["quality_explained/License: Open License"]
        item["quality_explained_ListType_Local"] = row["quality_explained/List type: Local"]
        item["quality_explained_ListType_Primary"] = row["quality_explained/List type: Primary"]
        item["quality_explained_ListType_Secondary"] = row["quality_explained/List type: Secondary"]
        item["quality_explained_ListType_ThirdParty"] = row["quality_explained/List type: Third Party"]
        item["registerType"] = row["registerType"]
        item["sector"] = row["sector"]
        item["structure"] = row["structure"]
        item["subnationalCoverage"] = row["subnationalCoverage"]
        item["url"] = row["url"]

        return item
