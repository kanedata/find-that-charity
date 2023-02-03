from datetime import date

from ninja import Schema


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
    DissolutionDate: date = None
    IncorporationDate: date = None
    Accounts_AccountRefDay: int = None
    Accounts_AccountRefMonth: int = None
    Accounts_NextDueDate: date = None
    Accounts_LastMadeUpDate: date = None
    Accounts_AccountCategory: str = None
    Returns_NextDueDate: date = None
    Returns_LastMadeUpDate: date = None
    Mortgages_NumMortCharges: int = None
    Mortgages_NumMortOutstanding: int = None
    Mortgages_NumMortPartSatisfied: int = None
    Mortgages_NumMortSatisfied: int = None
    LimitedPartnerships_NumGenPartners: int = None
    LimitedPartnerships_NumLimPartners: int = None
    URI: str = None
    ConfStmtNextDueDate: date = None
    ConfStmtLastMadeUpDate: date = None
    org_id: str = None
