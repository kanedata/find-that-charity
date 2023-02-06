from django.db import models

from ftc.models import EXTERNAL_LINKS, OrgidField


class SICCode(models.Model):
    org_id = OrgidField(db_index=True)
    code = models.CharField(max_length=255)
    scrape = models.ForeignKey(
        "ftc.Scrape",
        on_delete=models.DO_NOTHING,
    )
    spider = models.CharField(max_length=200, db_index=True, default="companies")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["org_id", "code"],
                name="unique_sic_code",
            )
        ]


class PreviousName(models.Model):
    org_id = OrgidField(db_index=True)
    ConDate = models.DateField(null=True, blank=True)
    CompanyName = models.CharField(max_length=255)
    scrape = models.ForeignKey(
        "ftc.Scrape",
        on_delete=models.DO_NOTHING,
    )
    spider = models.CharField(max_length=200, db_index=True, default="companies")

    def __str__(self):
        return "<Previous name {} for {}>".format(
            self.CompanyName, self.company.CompanyName
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["org_id", "CompanyName", "ConDate"],
                name="unique_previous_name",
            )
        ]


class AccountCategoryChoices(models.TextChoices):
    ACCOUNTS_TYPE_NOT_AVAILABLE = "ACCOUNTS TYPE NOT AVAILABLE"
    AUDIT_EXEMPTION_SUBSIDIARY = "AUDIT EXEMPTION SUBSIDIARY"
    AUDITED_ABRIDGED = "AUDITED ABRIDGED"
    DORMANT = "DORMANT"
    FILING_EXEMPTION_SUBSIDIARY = "FILING EXEMPTION SUBSIDIARY"
    FULL = "FULL"
    GROUP = "GROUP"
    MEDIUM = "MEDIUM"
    MICRO_ENTITY = "MICRO ENTITY"
    SMALL = "SMALL"
    TOTAL_EXEMPTION_FULL = "TOTAL EXEMPTION FULL"
    TOTAL_EXEMPTION_SMALL = "TOTAL EXEMPTION SMALL"
    UNAUDITED_ABRIDGED = "UNAUDITED ABRIDGED"
    NO_ACCOUNTS_FILED = "NO ACCOUNTS FILED"


class CompanyCategoryChoices(models.TextChoices):
    CIC = "Community Interest Company"
    CIO = "Charitable Incorporated Organisation"
    CLG = "PRI/LTD BY GUAR/NSC (Private, limited by guarantee, no share capital)"
    CLG_LIMITED = "PRI/LBG/NSC (Private, Limited by guarantee, no share capital, use of 'Limited' exemption)"
    CLOSED = "Converted/Closed"
    EURO_PLC = "European Public Limited-Liability Company (SE)"
    INVESTMENT_COMPANY_WITH_VARIABLE_CAPITAL = (
        "Investment Company with Variable Capital"
    )
    INVESTMENT_COMPANY_WITH_VARIABLE_CAPITAL_SECURITIES = (
        "Investment Company with Variable Capital (Securities)"
    )
    INVESTMENT_COMPANY_WITH_VARIABLE_CAPITAL_UMBRELLA = (
        "Investment Company with Variable Capital(Umbrella)"
    )
    IPS = "Industrial and Provident Society"
    LIMITED_PARTNERSHIP = "Limited Partnership"
    LLP = "Limited Liability Partnership"
    OLD_PUBLIC_COMPANY = "Old Public Company"
    OTHER_COMPANY_TYPE = "Other company type"
    PLC = "Public Limited Company"
    PRIVATE_LIMITED_COMPANY = "Private Limited Company"
    PRIVATE_LIMITED_COMPANY_SECT30 = (
        "PRIV LTD SECT. 30 (Private limited company, section 30 of the Companies Act)"
    )
    PRIVATE_UNLIMITED = "Private Unlimited"
    PRIVATE_UNLIMITED_COMPANY = "Private Unlimited Company"
    PROTECTED_CELL_COMPANY = "Protected Cell Company"
    RC = "Royal Charter Company"
    RS = "Registered Society"
    SCIO = "Scottish Charitable Incorporated Organisation"
    SCOTTISH_PARTNERSHIP = "Scottish Partnership"
    UNITED_KINGDOM_ECONOMIC_INTEREST_GROUPING = (
        "United Kingdom Economic Interest Grouping"
    )


class Account(models.Model):
    org_id = OrgidField(db_index=True)
    financial_year_end = models.DateField(db_index=True)
    category = models.CharField(
        max_length=255, db_index=True, choices=AccountCategoryChoices.choices
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["org_id", "financial_year_end"],
                name="unique_financial_year_end",
            )
        ]


class Company(models.Model):
    CompanyName = models.CharField(max_length=255, db_index=True)
    CompanyNumber = models.CharField(max_length=10, db_index=True, unique=True)
    RegAddress_CareOf = models.CharField(max_length=255, null=True, blank=True)
    RegAddress_POBox = models.CharField(max_length=255, null=True, blank=True)
    RegAddress_AddressLine1 = models.CharField(max_length=255, null=True, blank=True)
    RegAddress_AddressLine2 = models.CharField(max_length=255, null=True, blank=True)
    RegAddress_PostTown = models.CharField(max_length=255, null=True, blank=True)
    RegAddress_County = models.CharField(max_length=255, null=True, blank=True)
    RegAddress_Country = models.CharField(max_length=255, null=True, blank=True)
    RegAddress_PostCode = models.CharField(
        max_length=255, db_index=True, null=True, blank=True
    )
    CompanyCategory = models.CharField(
        max_length=255,
        db_index=True,
        null=True,
        blank=True,
        choices=CompanyCategoryChoices.choices,
    )
    CompanyStatus = models.CharField(
        max_length=255, db_index=True, null=True, blank=True
    )
    CountryOfOrigin = models.CharField(
        max_length=255, db_index=True, null=True, blank=True
    )
    DissolutionDate = models.DateField(db_index=True, null=True, blank=True)
    IncorporationDate = models.DateField(db_index=True, null=True, blank=True)
    Accounts_AccountRefDay = models.IntegerField(null=True, blank=True)
    Accounts_AccountRefMonth = models.IntegerField(null=True, blank=True)
    Accounts_NextDueDate = models.DateField(null=True, blank=True)
    Accounts_LastMadeUpDate = models.DateField(null=True, blank=True)
    Accounts_AccountCategory = models.CharField(
        max_length=255, null=True, blank=True, choices=AccountCategoryChoices.choices
    )
    Returns_NextDueDate = models.DateField(null=True, blank=True)
    Returns_LastMadeUpDate = models.DateField(null=True, blank=True)
    Mortgages_NumMortCharges = models.IntegerField(null=True, blank=True)
    Mortgages_NumMortOutstanding = models.IntegerField(null=True, blank=True)
    Mortgages_NumMortPartSatisfied = models.IntegerField(null=True, blank=True)
    Mortgages_NumMortSatisfied = models.IntegerField(null=True, blank=True)
    LimitedPartnerships_NumGenPartners = models.IntegerField(null=True, blank=True)
    LimitedPartnerships_NumLimPartners = models.IntegerField(null=True, blank=True)
    URI = models.URLField(max_length=255, null=True, blank=True)
    ConfStmtNextDueDate = models.DateField(null=True, blank=True)
    ConfStmtLastMadeUpDate = models.DateField(null=True, blank=True)
    org_id = OrgidField(db_index=True)
    scrape = models.ForeignKey(
        "ftc.Scrape",
        on_delete=models.DO_NOTHING,
    )
    spider = models.CharField(max_length=200, db_index=True, default="companies")

    @property
    def active(self):
        return self.CompanyStatus == "Active"

    @property
    def siccodes(self):
        return SICCode.objects.filter(org_id=self.org_id)

    @property
    def previous_names(self):
        return PreviousName.objects.filter(org_id=self.org_id)

    @property
    def accounts(self):
        return Account.objects.filter(org_id=self.org_id)

    def __str__(self):
        return "<Company {} [{}]>".format(self.CompanyName, self.CompanyNumber)

    def get_links(self):
        links = EXTERNAL_LINKS.get("GB-COH", [])
        for link in links:
            yield (link[0].format(self.org_id), link[1])
