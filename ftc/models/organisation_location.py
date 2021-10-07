from django.db import models

from .orgid import OrgidField


class OrganisationLocation(models.Model):
    class LocationTypes(models.TextChoices):
        REGISTERED_OFFICE = "HQ", "Registered Office"
        AREA_OF_OPERATION = "AOO", "Area of operation"
        SITE = "SITE", "Site"

    class GeoCodeTypes(models.TextChoices):
        POSTCODE = "PC", "UK Postcode"
        ONS_CODE = "ONS", "ONS code"
        ISO_CODE = "ISO", "ISO3166-1 Country Code"

    org_id = OrgidField(db_index=True, verbose_name="Organisation Identifier")
    name = models.CharField(max_length=255, verbose_name="Name")
    description = models.TextField(null=True, blank=True, verbose_name="Description")
    geoCode = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Geo Code"
    )
    geoCodeType = models.CharField(
        max_length=5,
        choices=GeoCodeTypes.choices,
        default=GeoCodeTypes.ONS_CODE,
        db_index=True,
        verbose_name="Geo Code Type",
    )
    locationType = models.CharField(
        max_length=5,
        choices=LocationTypes.choices,
        default=LocationTypes.REGISTERED_OFFICE,
        db_index=True,
        verbose_name="Location Type",
    )
    spider = models.CharField(max_length=200, db_index=True)
    source = models.ForeignKey(
        "Source",
        related_name="organisation_locations",
        on_delete=models.DO_NOTHING,
    )
    scrape = models.ForeignKey(
        "Scrape",
        related_name="organisation_locations",
        on_delete=models.DO_NOTHING,
    )

    # geography fields
    geo_iso = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        verbose_name="ISO3166-1 Country Code",
        db_index=True,
    )
    geo_oa11 = models.CharField(
        max_length=9, null=True, blank=True, verbose_name="Output Area"
    )
    geo_cty = models.CharField(
        max_length=9, null=True, blank=True, verbose_name="County"
    )
    geo_laua = models.CharField(
        max_length=9,
        null=True,
        blank=True,
        verbose_name="Local Authority",
        db_index=True,
    )
    geo_ward = models.CharField(
        max_length=9, null=True, blank=True, verbose_name="Ward"
    )
    geo_ctry = models.CharField(
        max_length=9, null=True, blank=True, verbose_name="Country", db_index=True
    )
    geo_rgn = models.CharField(
        max_length=9, null=True, blank=True, verbose_name="Region", db_index=True
    )
    geo_pcon = models.CharField(
        max_length=9,
        null=True,
        blank=True,
        verbose_name="Parliamentary Constituency",
        db_index=True,
    )
    geo_ttwa = models.CharField(
        max_length=9, null=True, blank=True, verbose_name="Travel to Work Area"
    )
    geo_lsoa11 = models.CharField(
        max_length=9,
        null=True,
        blank=True,
        verbose_name="Lower Super Output Area",
        db_index=True,
    )
    geo_msoa11 = models.CharField(
        max_length=9,
        null=True,
        blank=True,
        verbose_name="Middle Super Output Area",
        db_index=True,
    )
    geo_lep1 = models.CharField(
        max_length=9,
        null=True,
        blank=True,
        verbose_name="Local Enterprise Partnership 1",
    )
    geo_lep2 = models.CharField(
        max_length=9,
        null=True,
        blank=True,
        verbose_name="Local Enterprise Partnership 2",
    )
    geo_lat = models.FloatField(null=True, blank=True, verbose_name="Latitude")
    geo_long = models.FloatField(null=True, blank=True, verbose_name="Longitude")

    def __repr__(self):
        return "<Location {}/>".format(self.geoCode)

    class Meta:
        unique_together = (("org_id", "name", "geoCodeType", "locationType", "spider", "source_id", "scrape_id"),)
