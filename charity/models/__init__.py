from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.forms.models import model_to_dict

from .ccew import (
    CCEWCharity,
    CCEWCharityAnnualReturnHistory,
    CCEWCharityAreaOfOperation,
    CCEWCharityARPartA,
    CCEWCharityARPartB,
    CCEWCharityClassification,
    CCEWCharityEventHistory,
    CCEWCharityGoverningDocument,
    CCEWCharityOtherNames,
    CCEWCharityOtherRegulators,
    CCEWCharityPolicy,
    CCEWCharityPublishedReport,
    CCEWCharityTrustee,
)


class Charity(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, db_index=True)
    constitution = models.TextField(null=True, blank=True)
    geographical_spread = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    postcode = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(db_index=True)
    date_registered = models.DateField(null=True, blank=True, db_index=True)
    date_removed = models.DateField(null=True, blank=True, db_index=True)
    removal_reason = models.CharField(max_length=255, null=True, blank=True)
    web = models.URLField(null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    company_number = models.CharField(max_length=255, null=True, blank=True)
    activities = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    first_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    income = models.BigIntegerField(null=True, blank=True, db_index=True)
    spending = models.BigIntegerField(null=True, blank=True)
    latest_fye = models.DateField(null=True, blank=True)
    employees = models.IntegerField(null=True, blank=True, db_index=True)
    volunteers = models.IntegerField(null=True, blank=True)
    trustees = models.IntegerField(null=True, blank=True)
    dual_registered = models.BooleanField(null=True, blank=True)

    areas_of_operation = models.ManyToManyField("AreaOfOperation")

    class Meta:
        verbose_name_plural = "Charities"

    def __str__(self):
        return "{} [{}]".format(self.name, self.id)

    def financial_json(self):
        return [
            {
                **model_to_dict(f),
                "exp_gen": f.exp_gen,
                "reserves_months": f.reserves_months,
                "fyend": f.fyend.isoformat(),
                "fystart": f.fystart.isoformat() if f.fystart else None,
            }
            for f in self.financial.order_by("fyend").all()
        ]

    @property
    def has_ccew_partb(self):
        for f in self.financial.all():
            if f.has_ccew_partb:
                return True
        return False


class CharityName(models.Model):
    charity = models.ForeignKey(
        "Charity", on_delete=models.CASCADE, related_name="other_names"
    )
    name = models.CharField(max_length=255, db_index=True)
    normalisedName = models.CharField(
        max_length=255, db_index=True, blank=True, null=True
    )
    name_type = models.CharField(max_length=255, db_index=True)

    class Meta:
        unique_together = (
            "charity",
            "name",
        )

    def __str__(self):
        return "{} [{}]".format(self.name, self.charity.id)


class CharityFinancial(models.Model):
    class AccountType(models.TextChoices):
        BASIC = "basic", "Basic"
        CONSOLIDATED = "consolidated", "Consolidated"
        CHARITY = "charity", "Charity"
        BASIC_OSCR = "basic_oscr", "Basic (OSCR)"
        DETAILED_OSCR = "detailed_oscr", "Detailed (OSCR)"
        BASIC_CCNI = "basic_ccni", "Basic (CCNI)"
        DETAILED_CCNI = "detailed_ccni", "Detailed (CCNI)"

    charity = models.ForeignKey(
        "Charity", on_delete=models.CASCADE, related_name="financial"
    )
    fyend = models.DateField(db_index=True)
    fystart = models.DateField(null=True, blank=True)
    income = models.BigIntegerField(null=True, blank=True)
    spending = models.BigIntegerField(null=True, blank=True)
    inc_leg = models.BigIntegerField(null=True, blank=True)
    inc_end = models.BigIntegerField(null=True, blank=True)
    inc_vol = models.BigIntegerField(null=True, blank=True)
    inc_fr = models.BigIntegerField(null=True, blank=True)
    inc_char = models.BigIntegerField(null=True, blank=True)
    inc_invest = models.BigIntegerField(null=True, blank=True)
    inc_other = models.BigIntegerField(null=True, blank=True)
    inc_total = models.BigIntegerField(null=True, blank=True)
    invest_gain = models.BigIntegerField(null=True, blank=True)
    asset_gain = models.BigIntegerField(null=True, blank=True)
    pension_gain = models.BigIntegerField(null=True, blank=True)
    exp_vol = models.BigIntegerField(null=True, blank=True)
    exp_trade = models.BigIntegerField(null=True, blank=True)
    exp_invest = models.BigIntegerField(null=True, blank=True)
    exp_grant = models.BigIntegerField(null=True, blank=True)
    exp_charble = models.BigIntegerField(null=True, blank=True)
    exp_gov = models.BigIntegerField(null=True, blank=True)
    exp_other = models.BigIntegerField(null=True, blank=True)
    exp_total = models.BigIntegerField(null=True, blank=True)
    exp_support = models.BigIntegerField(null=True, blank=True)
    exp_dep = models.BigIntegerField(null=True, blank=True)
    reserves = models.BigIntegerField(null=True, blank=True)
    asset_open = models.BigIntegerField(null=True, blank=True)
    asset_close = models.BigIntegerField(null=True, blank=True)
    fixed_assets = models.BigIntegerField(null=True, blank=True)
    open_assets = models.BigIntegerField(null=True, blank=True)
    invest_assets = models.BigIntegerField(null=True, blank=True)
    cash_assets = models.BigIntegerField(null=True, blank=True)
    current_assets = models.BigIntegerField(null=True, blank=True)
    credit_1 = models.BigIntegerField(null=True, blank=True)
    credit_long = models.BigIntegerField(null=True, blank=True)
    pension_assets = models.BigIntegerField(null=True, blank=True)
    total_assets = models.BigIntegerField(null=True, blank=True)
    funds_end = models.BigIntegerField(null=True, blank=True)
    funds_restrict = models.BigIntegerField(null=True, blank=True)
    funds_unrestrict = models.BigIntegerField(null=True, blank=True)
    funds_total = models.BigIntegerField(null=True, blank=True)
    employees = models.BigIntegerField(null=True, blank=True)
    volunteers = models.BigIntegerField(null=True, blank=True)
    account_type = models.CharField(
        max_length=50, default=AccountType.BASIC, choices=AccountType.choices
    )

    class Meta:
        unique_together = (
            "charity",
            "fyend",
        )

    def __str__(self):
        return "{} {}".format(self.charity.name, self.fyend)

    @property
    def has_ccew_partb(self):
        return self.account_type in (
            CharityFinancial.AccountType.CHARITY,
            CharityFinancial.AccountType.CONSOLIDATED,
        )

    @property
    def exp_gen(self):
        """Expenditure on generating funds"""
        if self.exp_total and self.has_ccew_partb:
            return self.exp_total - (self.exp_other + self.exp_gov + self.exp_charble)

    @property
    def reserves_months(self):
        if self.exp_total and self.reserves:
            return (self.reserves / self.exp_total) * 12


class CharityRaw(models.Model):
    org_id = models.CharField(max_length=255, db_index=True)
    spider = models.CharField(max_length=255, db_index=True)
    scrape = models.ForeignKey(
        "ftc.Scrape",
        on_delete=models.CASCADE,
    )
    data = models.JSONField(encoder=DjangoJSONEncoder)

    class Meta:
        verbose_name = "Raw charity data"
        verbose_name_plural = "Raw charity data"

    def __str__(self):
        return "{} {}".format(self.spider, self.org_id)


class AreaOfOperation(models.Model):
    aootype = models.CharField(max_length=1, null=True, blank=True)
    aookey = models.IntegerField(null=True, blank=True)
    aooname = models.CharField(max_length=255, db_index=True)
    aoosort = models.CharField(max_length=255, db_index=True)
    welsh = models.BooleanField(verbose_name="In Wales", null=True, blank=True)
    master = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        verbose_name="Parent area",
        null=True,
        blank=True,
    )
    GSS = models.CharField(
        verbose_name="ONS Geocode for Local Authority",
        max_length=10,
        null=True,
        blank=True,
        db_index=True,
    )
    ISO3166_1 = models.CharField(
        verbose_name="ISO3166-1 country code (2 character)",
        max_length=2,
        null=True,
        blank=True,
        db_index=True,
    )
    ISO3166_1_3 = models.CharField(
        verbose_name="ISO3166-1 country code (3 character)",
        max_length=3,
        null=True,
        blank=True,
        db_index=True,
    )
    ISO3166_2_GB = models.CharField(
        verbose_name="ISO3166-2 region code (GB only)",
        max_length=6,
        null=True,
        blank=True,
        db_index=True,
    )
    ContinentCode = models.CharField(
        verbose_name="Continent", max_length=2, null=True, blank=True, db_index=True
    )

    class Meta:
        verbose_name = "Area of operation"
        verbose_name_plural = "Areas of operation"

    def __str__(self):
        return self.aooname


__all__ = (
    Charity,
    CharityName,
    CharityFinancial,
    CharityRaw,
    AreaOfOperation,
    CCEWCharity,
    CCEWCharityAnnualReturnHistory,
    CCEWCharityAreaOfOperation,
    CCEWCharityARPartA,
    CCEWCharityARPartB,
    CCEWCharityClassification,
    CCEWCharityEventHistory,
    CCEWCharityGoverningDocument,
    CCEWCharityOtherNames,
    CCEWCharityOtherRegulators,
    CCEWCharityPolicy,
    CCEWCharityPublishedReport,
    CCEWCharityTrustee,
)
