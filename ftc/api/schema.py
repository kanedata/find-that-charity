import datetime
from typing import List

from ninja import Schema


class OrganisationType(Schema):
    slug: str
    title: str


class Source(Schema):
    id: str
    title: str
    publisher: str
    data: dict = None


class OrgIdScheme(Schema):
    code: str
    data: dict
    priority: int = None


class Address(Schema):
    streetAddress: str = None
    addressLocality: str = None
    addressRegion: str = None
    addressCountry: str = None
    postalCode: str = None


class OrganisationLink(Schema):
    orgid: str = None
    url: str = None


class OrganisationWebsiteLink(Schema):
    site: str = None
    orgid: str = None
    url: str = None


class Location(Schema):
    id: str = None
    name: str = None
    geocode: str = None
    type: str = None


class Organisation(Schema):
    id: str
    name: str
    charityNumber: str = None
    companyNumber: str = None
    description: str = None
    url: str = None

    # finances
    latestFinancialYearEnd: datetime.date = None
    latestIncome: int = None
    latestSpending: int = None
    latestEmployees: int = None
    latestVolunteers: int = None
    trusteeCount: int = None

    dateRegistered: datetime.date = None
    dateRemoved: datetime.date = None
    active: bool = None

    parent: str = None
    organisationType: List[str] = None
    organisationTypePrimary: OrganisationType = None
    alternateName: List[str] = None
    telephone: str = None
    email: str = None

    location: List[dict] = None
    address: Address = None

    sources: List[str] = None
    links: List[OrganisationWebsiteLink] = None
    orgIDs: List[str] = None
    linked_records: List[OrganisationLink] = None

    dateModified: datetime.datetime = None

    # domain: str = None
    # status: str = None
    # source_id: str
    # # scrape: str = None
    # spider: str = None
    # # org_id_scheme: OrgIdScheme = None

    # # geography fields
    # geo_oa11: str = None
    # geo_cty: str = None
    # geo_laua: str = None
    # geo_ward: str = None
    # geo_ctry: str = None
    # geo_rgn: str = None
    # geo_pcon: str = None
    # geo_ttwa: str = None
    # geo_lsoa11: str = None
    # geo_msoa11: str = None
    # geo_lep1: str = None
    # geo_lep2: str = None
    # geo_lat: float = None
    # geo_long: float = None
