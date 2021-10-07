from compositefk.fields import CompositeForeignKey
from django.db import models
from django_better_admin_arrayfield.models.fields import ArrayField

from ftc.models import OrgidField


class GenderPayGap(models.Model):
    class EmployerSizeChoices(models.TextChoices):
        LESS_THAN_250 = "Less than 250"
        FROM_250_TO_499 = "250 to 499"
        FROM_500_TO_999 = "500 to 999"
        FROM_1000_TO_4999 = "1000 to 4999"
        FROM_5000_TO_19999 = "5000 to 19,999"

    org_id = OrgidField(
        db_index=True, verbose_name="Organisation Identifier", null=True, blank=True
    )
    Year = models.IntegerField(db_index=True)
    EmployerName = models.CharField(db_index=True, max_length=255)
    EmployerId = models.CharField(db_index=True, max_length=255)
    Address = models.CharField(max_length=255, null=True, blank=True)
    PostCode = models.CharField(max_length=255, null=True, blank=True)
    CompanyNumber = models.CharField(
        db_index=True, max_length=255, null=True, blank=True
    )
    SicCodes = ArrayField(models.CharField(max_length=100), null=True, blank=True)
    DiffMeanHourlyPercent = models.FloatField(null=True, blank=True)
    DiffMedianHourlyPercent = models.FloatField(null=True, blank=True)
    DiffMeanBonusPercent = models.FloatField(null=True, blank=True)
    DiffMedianBonusPercent = models.FloatField(null=True, blank=True)
    MaleBonusPercent = models.FloatField(null=True, blank=True)
    FemaleBonusPercent = models.FloatField(null=True, blank=True)
    MaleLowerQuartile = models.FloatField(null=True, blank=True)
    FemaleLowerQuartile = models.FloatField(null=True, blank=True)
    MaleLowerMiddleQuartile = models.FloatField(null=True, blank=True)
    FemaleLowerMiddleQuartile = models.FloatField(null=True, blank=True)
    MaleUpperMiddleQuartile = models.FloatField(null=True, blank=True)
    FemaleUpperMiddleQuartile = models.FloatField(null=True, blank=True)
    MaleTopQuartile = models.FloatField(null=True, blank=True)
    FemaleTopQuartile = models.FloatField(null=True, blank=True)
    CompanyLinkToGPGInfo = models.URLField(null=True, blank=True, max_length=1000)
    ResponsiblePerson = models.CharField(max_length=255, null=True, blank=True)
    EmployerSize = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        choices=EmployerSizeChoices.choices,
    )
    CurrentName = models.CharField(max_length=255, null=True, blank=True)
    SubmittedAfterTheDeadline = models.BooleanField(null=True, blank=True)
    DueDate = models.DateField(null=True, blank=True)
    DateSubmitted = models.DateField(null=True, blank=True)
    scrape = models.ForeignKey(
        "ftc.Scrape",
        on_delete=models.DO_NOTHING,
    )
    spider = models.CharField(max_length=200, db_index=True, default="gpg")

    def __str__(self):
        return "<GenderPayGap '{}' [{}]>".format(self.EmployerName, self.Year)


class CQCProviderType(models.TextChoices):
    SOCIAL_CARE = "Social Care Org"
    INDEPENDENT_HEALTHCARE = "Independent Healthcare Org"
    PRIMARY_DENTAL_CARE = "Primary Dental Care"
    PRIMARY_MEDICAL_SERVICES = "Primary Medical Services"
    INDEPENDENT_AMBULANCE = "Independent Ambulance"
    NHS_HEALTHCASE_ORGANISATION = "NHS Healthcare Organisation"


class CQCInspectionDirectorate(models.TextChoices):
    ADULT_SOCIAL_CARE = "Adult social care"
    HOSPITALS = "Hospitals"
    PRIMARY_MEDICAL_SERVICES = "Primary medical services"
    UNSPECIFIED = "Unspecified"


class CQCOwnershipType(models.TextChoices):
    ORGANISATION = "Organisation"
    INDIVIDUAL = "Individual"
    PARTNERSHIP = "Partnership"
    NHS_BODY = "NHS Body"


class CQCRatings(models.TextChoices):
    INADEQUATE = "Inadequate"
    REQUIRES_IMPROVEMENT = "Requires improvement"
    GOOD = "Good"
    OUTSTANDING = "Outstanding"


class CQCProvider(models.Model):
    class ProviderStatus(models.TextChoices):
        REGISTERED = "Registered"
        DEREGISTERED_E = "Deregistered (E)"
        DEREGISTERED_V = "Deregistered (V)"
        DISSOLVED = "Dissolved"
        REMOVED = "Removed"

    company_number = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Provider Companies House Number",
    )
    charity_number = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Provider Charity Number"
    )
    org_id = OrgidField(
        db_index=True, verbose_name="Organisation Identifier", null=True, blank=True
    )
    record_id = models.BigAutoField(primary_key=True)
    id = models.CharField(max_length=255, verbose_name="Provider ID")
    name = models.CharField(max_length=255, verbose_name="Provider Name")
    start_date = models.DateField(
        null=True, blank=True, verbose_name="Provider HSCA start date"
    )
    end_date = models.DateField(
        null=True, blank=True, default=None, verbose_name="Provider HSCA End Date"
    )
    status = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Provider Status",
        choices=ProviderStatus.choices,
        default=ProviderStatus.REGISTERED,
    )
    sector = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Provider Type/Sector",
        choices=CQCProviderType.choices,
    )
    directorate = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Provider Inspection Directorate",
        choices=CQCInspectionDirectorate.choices,
    )
    inspection_category = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Provider Primary Inspection Category",
    )
    ownership_type = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Provider Ownership Type",
        choices=CQCOwnershipType.choices,
    )
    telephone = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Provider Telephone Number"
    )
    web = models.URLField(
        null=True, blank=True, max_length=255, verbose_name="Provider Web Address"
    )
    address_street = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Provider Street Address"
    )
    address_2 = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Provider Address Line 2"
    )
    address_city = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Provider City"
    )
    address_county = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Provider County"
    )
    address_postcode = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Provider Postal Code"
    )
    geo_uprn = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Provider PAF / UPRN ID"
    )
    geo_local_authority = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Provider Local Authority"
    )
    geo_region = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Provider Region"
    )
    geo_latitude = models.FloatField(
        null=True, blank=True, verbose_name="Provider Latitude"
    )
    geo_longitude = models.FloatField(
        null=True, blank=True, verbose_name="Provider Longitude"
    )
    geo_pcon = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Provider Parliamentary Constituency",
    )
    scrape = models.ForeignKey(
        "ftc.Scrape",
        on_delete=models.DO_NOTHING,
    )
    spider = models.CharField(max_length=200, db_index=True, default="cqc")
    brand_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )
    brand = CompositeForeignKey(
        "CQCBrand",
        on_delete=models.DO_NOTHING,
        to_fields={"id": "brand_id", "scrape_id": "scrape_id"},
        null=True,
        blank=True,
    )


class CQCBrand(models.Model):
    record_id = models.BigAutoField(primary_key=True)
    id = models.CharField(max_length=255, verbose_name="Brand ID")
    name = models.CharField(max_length=255, verbose_name="Brand Name")
    scrape = models.ForeignKey(
        "ftc.Scrape",
        on_delete=models.DO_NOTHING,
    )
    spider = models.CharField(max_length=200, db_index=True, default="cqc")


class CQCLocation(models.Model):
    class LocationStatus(models.TextChoices):
        ACTIVE = "Active"
        INACTIVE = "Inactive-Dereg"
        REMOVED = "Removed"

    record_id = models.BigAutoField(primary_key=True)
    id = models.CharField(max_length=255, verbose_name="Location ID")
    start_date = models.DateField(
        null=True, blank=True, verbose_name="Location HSCA start date"
    )
    end_date = models.DateField(
        null=True, blank=True, default=None, verbose_name="Location HSCA End Date"
    )
    status = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Location Status",
        choices=LocationStatus.choices,
        default=LocationStatus.ACTIVE,
    )
    care_home = models.BooleanField(null=True, blank=True, verbose_name="Care home?")
    name = models.CharField(max_length=255, verbose_name="Location Name")
    ods_code = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Location ODS Code"
    )
    telephone = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Location Telephone Number"
    )
    web = models.URLField(
        null=True, blank=True, max_length=255, verbose_name="Location Web Address"
    )
    care_home_beds = models.IntegerField(
        null=True, blank=True, verbose_name="Care homes beds"
    )
    sector = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Location Type/Sector",
        choices=CQCProviderType.choices,
    )
    directorate = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Location Inspection Directorate",
        choices=CQCInspectionDirectorate.choices,
    )
    inspection_category = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Location Primary Inspection Category",
    )
    latest_overall_rating = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Location Latest Overall Rating",
        choices=CQCRatings.choices,
    )
    publication_date = models.DateField(
        null=True, blank=True, verbose_name="Publication Date"
    )
    inherited_rating = models.BooleanField(
        null=True, blank=True, verbose_name="Inherited Rating (Y/N)"
    )
    geo_region = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Location Region"
    )
    geo_local_authority = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Location Local Authority"
    )
    geo_onspd_ccg_code = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Location ONSPD CCG Code"
    )
    geo_onspd_ccg = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Location ONSPD CCG"
    )
    geo_commissioning_ccg_code = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Location Commissioning CCG Code",
    )
    geo_commissioning_ccg = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Location Commissioning CCG"
    )
    address_street = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Location Street Address"
    )
    address_2 = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Location Address Line 2"
    )
    address_city = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Location City"
    )
    address_county = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Location County"
    )
    address_postcode = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Location Postal Code"
    )
    geo_uprn = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Location PAF / UPRN ID"
    )
    geo_latitude = models.FloatField(
        null=True, blank=True, verbose_name="Location Latitude"
    )
    geo_longitude = models.FloatField(
        null=True, blank=True, verbose_name="Location Longitude"
    )
    geo_pcon = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Location Parliamentary Constituency",
    )
    scrape = models.ForeignKey(
        "ftc.Scrape",
        on_delete=models.DO_NOTHING,
    )
    spider = models.CharField(max_length=200, db_index=True, default="cqc")
    provider_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )
    provider = CompositeForeignKey(
        "CQCProvider",
        related_name="locations",
        on_delete=models.DO_NOTHING,
        to_fields={"id": "provider_id", "scrape_id": "scrape_id"},
        null=True,
        blank=True,
    )
    classification = models.ManyToManyField("charity.VocabularyEntries")
