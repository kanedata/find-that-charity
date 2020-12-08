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


class Organisation(Schema):
    org_id: str
    orgIDs: List[str] = None
    linked_orgs: List[str] = None
    name: str
    alternateName: List[str] = None
    charityNumber: str = None
    companyNumber: str = None
    streetAddress: str = None
    addressLocality: str = None
    addressRegion: str = None
    addressCountry: str = None
    postalCode: str = None
    telephone: str = None
    email: str = None
    description: str = None
    url: str = None
    domain: str = None
    latestIncome: int = None
    latestIncomeDate: datetime.date = None
    dateRegistered: datetime.date = None
    dateRemoved: datetime.date = None
    active: bool = None
    status: str = None
    parent: str = None
    dateModified: datetime.datetime = None
    source_id: str
    organisationType: List[str] = None
    organisationTypePrimary: OrganisationType = None
    # scrape: str = None
    spider: str = None
    location: List[dict] = None
    # org_id_scheme: OrgIdScheme = None

    # geography fields
    geo_oa11: str = None
    geo_cty: str = None
    geo_laua: str = None
    geo_ward: str = None
    geo_ctry: str = None
    geo_rgn: str = None
    geo_pcon: str = None
    geo_ttwa: str = None
    geo_lsoa11: str = None
    geo_msoa11: str = None
    geo_lep1: str = None
    geo_lep2: str = None
    geo_lat: float = None
    geo_long: float = None
