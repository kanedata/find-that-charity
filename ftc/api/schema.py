import datetime
from typing import List, Optional

from ninja import Field, Schema


class OrganisationType(Schema):
    slug: str
    title: str


class Source(Schema):
    id: str
    title: str
    publisher: str
    data: Optional[dict] = None


class OrgIdScheme(Schema):
    code: str
    data: dict
    priority: Optional[int] = None


class Address(Schema):
    streetAddress: Optional[str] = None
    addressLocality: Optional[str] = None
    addressRegion: Optional[str] = None
    addressCountry: Optional[str] = None
    postalCode: Optional[str] = None


class OrganisationLink(Schema):
    orgid: Optional[str] = None
    url: Optional[str] = None


class OrganisationWebsiteLink(Schema):
    site: Optional[str] = None
    orgid: Optional[str] = None
    url: Optional[str] = None


class Location(Schema):
    id: Optional[str] = None
    name: Optional[str] = None
    geocode: Optional[str] = None
    type: Optional[str] = None


class Organisation(Schema):
    id: str = Field(alias="org_id")
    name: str
    charityNumber: Optional[str] = None
    companyNumber: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None

    # finances
    latestFinancialYearEnd: Optional[datetime.date] = None
    latestIncome: Optional[int] = None
    latestSpending: Optional[int] = None
    latestEmployees: Optional[int] = None
    latestVolunteers: Optional[int] = None
    trusteeCount: Optional[int] = None

    dateRegistered: Optional[datetime.date] = None
    dateRemoved: Optional[datetime.date] = None
    active: Optional[bool] = None

    parent: Optional[str] = None
    organisationType: Optional[List[str]] = None
    organisationTypePrimary: Optional[OrganisationType] = None
    alternateName: Optional[List[str]] = None
    telephone: Optional[str] = None
    email: Optional[str] = None

    location: Optional[List[dict]] = None
    address: Optional[Address] = None

    sources: Optional[List[str]] = None
    links: List[OrganisationWebsiteLink] = None
    orgIDs: Optional[List[str]] = None
    linked_records: List[OrganisationLink] = None

    dateModified: Optional[datetime.datetime] = None

    # domain: Optional[str] = None
    # status: Optional[str] = None
    # source_id: str
    # # scrape: Optional[str] = None
    # spider: Optional[str] = None
    # # org_id_scheme: Optional[OrgIdScheme] = None

    # # geography fields
    # geo_oa11: Optional[str] = None
    # geo_cty: Optional[str] = None
    # geo_laua: Optional[str] = None
    # geo_ward: Optional[str] = None
    # geo_ctry: Optional[str] = None
    # geo_rgn: Optional[str] = None
    # geo_pcon: Optional[str] = None
    # geo_ttwa: Optional[str] = None
    # geo_lsoa11: Optional[str] = None
    # geo_msoa11: Optional[str] = None
    # geo_lep1: Optional[str] = None
    # geo_lep2: Optional[str] = None
    # geo_lat: Optional[float] = None
    # geo_long: Optional[float] = None


class Company(Schema):
    CompanyName: Optional[str] = None
    CompanyNumber: Optional[str] = None
    RegAddress_CareOf: Optional[str] = None
    RegAddress_POBox: Optional[str] = None
    RegAddress_AddressLine1: Optional[str] = None
    RegAddress_AddressLine2: Optional[str] = None
    RegAddress_PostTown: Optional[str] = None
    RegAddress_County: Optional[str] = None
    RegAddress_Country: Optional[str] = None
    RegAddress_PostCode: Optional[str] = None
    CompanyCategory: Optional[str] = None
    CompanyStatus: Optional[str] = None
    CountryOfOrigin: Optional[str] = None
    DissolutionDate: Optional[datetime.date] = None
    IncorporationDate: Optional[datetime.date] = None
    Accounts_AccountRefDay: Optional[int] = None
    Accounts_AccountRefMonth: Optional[int] = None
    Accounts_NextDueDate: Optional[datetime.date] = None
    Accounts_LastMadeUpDate: Optional[datetime.date] = None
    Accounts_AccountCategory: Optional[str] = None
    Returns_NextDueDate: Optional[datetime.date] = None
    Returns_LastMadeUpDate: Optional[datetime.date] = None
    Mortgages_NumMortCharges: Optional[int] = None
    Mortgages_NumMortOutstanding: Optional[int] = None
    Mortgages_NumMortPartSatisfied: Optional[int] = None
    Mortgages_NumMortSatisfied: Optional[int] = None
    LimitedPartnerships_NumGenPartners: Optional[int] = None
    LimitedPartnerships_NumLimPartners: Optional[int] = None
    ConfStmtNextDueDate: Optional[datetime.date] = None
    ConfStmtLastMadeUpDate: Optional[datetime.date] = None
    org_id: Optional[str] = None
