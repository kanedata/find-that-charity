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


class OrganisationGroup(Schema):
    org_id: str
    # complete_names: List[str] = None
    orgIDs: List[str] = None
    # ids: List[str] = None
    name: str = None
    # sortname: str = None
    alternateName: List[str] = None
    postalCode: str = None
    domain: List[str] = None
    active: bool = None
    organisationType: List[str] = None
    organisationTypePrimary: str = None
    source: List[str] = None
    locations: List[str] = None
    # search_scale: float = None
    # dateModified: datetime.datetime = None
    score: int = None


{
    "search_scale": 16.8310800230497,
    "postalCode": "N1 9RL",
    "active": True,
    "alternateName": [
        "NCVO",
        "NATIONAL COUNCIL FOR VOLUNTARY ORGANISATIONS(THE)",
        "NATIONAL ASSOCIATION OF WOMEN'S CLUBS",
        "National Council for Voluntary Organisations",
        "NATIONAL OLD PEOPLES' WELFARE COUNCIL",
        "THE NATIONAL COUNCIL OF SOCIAL SERVICES",
        "NATIONAL FEDERATION OF COMMUNITY ORGANISATIONS",
        "VOLUNTEERING ENGLAND",
    ],
    "dateModified": "2022-07-01T13:29:36.633495+00:00",
    "source": ["ccew", "companies", "ror"],
    "organisationType": [
        "registered-charity",
        "registered-charity-england-and-wales",
        "registered-company",
        "incorporated-charity",
        "company-limited-by-guarantee",
        "nonprofit-institution",
    ],
    "sortname": "national council for voluntary organisations",
    "orgIDs": [
        "GB-CHC-1102770",
        "XI-GRID-grid.436857.b",
        "GB-COH-00198344",
        "GB-CHC-225922",
        "XI-ROR-01f3f2284",
    ],
    "org_id": "GB-CHC-225922",
    "domain": ["ncvo.org.uk", "ncvo.org.uk"],
    "name": "THE NATIONAL COUNCIL FOR VOLUNTARY ORGANISATIONS",
    "ids": [
        "1102770",
        "grid.436857.b",
        "00198344",
        "225922",
        "01f3f2284",
        "198344",
        "1f3f2284",
    ],
    "locations": [
        "E30000234",
        "GB",
        "E37000023",
        "E14000764",
        "E92000001",
        "E01002710",
        "E05000368",
        "E13000001",
        "E12000007",
        "E09000019",
        "E00013485",
        "E02000572",
    ],
    "organisationTypePrimary": "registered-charity",
}


class Company(Schema):
    CompanyName: str = None
    CompanyNumber: str = None
    RegAddress_CareOf: str = None
    RegAddress_POBox: str = None
    RegAddress_AddressLine1: str = None
    RegAddress_AddressLine2: str = None
    RegAddress_PostTown: str = None
    RegAddress_County: str = None
    RegAddress_Country: str = None
    RegAddress_PostCode: str = None
    CompanyCategory: str = None
    CompanyStatus: str = None
    CountryOfOrigin: str = None
    DissolutionDate: datetime.date = None
    IncorporationDate: datetime.date = None
    Accounts_AccountRefDay: int = None
    Accounts_AccountRefMonth: int = None
    Accounts_NextDueDate: datetime.date = None
    Accounts_LastMadeUpDate: datetime.date = None
    Accounts_AccountCategory: str = None
    Returns_NextDueDate: datetime.date = None
    Returns_LastMadeUpDate: datetime.date = None
    Mortgages_NumMortCharges: int = None
    Mortgages_NumMortOutstanding: int = None
    Mortgages_NumMortPartSatisfied: int = None
    Mortgages_NumMortSatisfied: int = None
    LimitedPartnerships_NumGenPartners: int = None
    LimitedPartnerships_NumLimPartners: int = None
    ConfStmtNextDueDate: datetime.date = None
    ConfStmtLastMadeUpDate: datetime.date = None
    org_id: str = None
