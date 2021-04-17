from django.db import models


class Postcode(models.Model):
    class UserType(models.IntegerChoices):
        SMALL = 0, "Small users"
        LARGE = 1, "Large users"
        __empty__ = "Unknown"

    class GridIndex(models.IntegerChoices):
        # Grid reference positional quality indicator
        BUILDING = (
            1,
            "within the building of the matched address closest to the postcode mean",
        )
        BUILDING_VISUAL = (
            2,
            "as for status value 1, except by visual inspection of Landline maps (Scotland only)",
        )
        APPROXIMATE = 3, "approximate to within 50 metres;"
        UNIT_MEAN = (
            4,
            "postcode unit mean (mean of matched addresses with the same postcode, but not snapped to a building)",
        )
        IMPUTED = (
            5,
            "imputed by ONS, by reference to surrounding postcode grid references",
        )
        SECTOR_MEAN = 6, "postcode sector mean, (mainly PO Boxes)"
        TERMINATED = (
            8,
            "postcode terminated prior to Gridlink® initiative, last known ONS postcode grid reference",
        )
        NOT_AVAILABLE = 9, "no grid reference available"

    pcd = models.CharField(max_length=7, unique=True)
    pcd2 = models.CharField(max_length=8, unique=True)
    pcds = models.CharField(max_length=8, unique=True, db_index=True)
    dointr = models.DateField()
    doterm = models.DateField(null=True, blank=True)
    usertype = models.IntegerField(choices=UserType.choices)
    oseast1m = models.IntegerField(null=True, blank=True)
    osnrth1m = models.IntegerField(null=True, blank=True)
    osgrdind = models.IntegerField(choices=GridIndex.choices)
    oa11 = models.CharField(max_length=9, null=True, blank=True)
    cty = models.CharField(max_length=9, null=True, blank=True)
    ced = models.CharField(max_length=9, null=True, blank=True)
    laua = models.CharField(max_length=9, null=True, blank=True)
    ward = models.CharField(max_length=9, null=True, blank=True)
    hlthau = models.CharField(max_length=9, null=True, blank=True)
    nhser = models.CharField(max_length=9, null=True, blank=True)
    ctry = models.CharField(max_length=9, null=True, blank=True)
    rgn = models.CharField(max_length=9, null=True, blank=True)
    pcon = models.CharField(max_length=9, null=True, blank=True)
    eer = models.CharField(max_length=9, null=True, blank=True)
    teclec = models.CharField(max_length=9, null=True, blank=True)
    ttwa = models.CharField(max_length=9, null=True, blank=True)
    pct = models.CharField(max_length=9, null=True, blank=True)
    nuts = models.CharField(max_length=9, null=True, blank=True)
    npark = models.CharField(max_length=9, null=True, blank=True)
    lsoa11 = models.CharField(max_length=9, null=True, blank=True)
    msoa11 = models.CharField(max_length=9, null=True, blank=True)
    wz11 = models.CharField(max_length=9, null=True, blank=True)
    ccg = models.CharField(max_length=9, null=True, blank=True)
    bua11 = models.CharField(max_length=9, null=True, blank=True)
    buasd11 = models.CharField(max_length=9, null=True, blank=True)
    ru11ind = models.CharField(max_length=2, null=True, blank=True)
    oac11 = models.CharField(max_length=3, null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    long = models.FloatField(null=True, blank=True)
    lep1 = models.CharField(max_length=9, null=True, blank=True)
    lep2 = models.CharField(max_length=9, null=True, blank=True)
    pfa = models.CharField(max_length=9, null=True, blank=True)
    imd = models.IntegerField(null=True, blank=True)
    calncv = models.CharField(max_length=9, null=True, blank=True)
    stp = models.CharField(max_length=9, null=True, blank=True)


class GeoLookup(models.Model):
    geoCode = models.CharField(
        max_length=200,
        verbose_name="Geo Code",
        primary_key=True,
    )
    geoCodeType = models.CharField(
        max_length=25,
        db_index=True,
        verbose_name="Geo Code Type",
    )
    name = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    geo_iso = models.CharField(
        max_length=3,
        verbose_name="ISO3166-1 Country Code",
        db_index=True,
        default="GB",
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
