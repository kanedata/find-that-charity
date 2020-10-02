from django.db import models


class Postcode(models.Model):

    class UserType(models.IntegerChoices):
        SMALL = 0, 'Small users'
        LARGE = 1, 'Large users'
        __empty__ = 'Unknown'

    class GridIndex(models.IntegerChoices):
        # Grid reference positional quality indicator
        BUILDING = 1, 'within the building of the matched address closest to the postcode mean'
        BUILDING_VISUAL = 2, 'as for status value 1, except by visual inspection of Landline maps (Scotland only)'
        APPROXIMATE = 3, 'approximate to within 50 metres;'
        UNIT_MEAN = 4, 'postcode unit mean (mean of matched addresses with the same postcode, but not snapped to a building)'
        IMPUTED = 5, 'imputed by ONS, by reference to surrounding postcode grid references'
        SECTOR_MEAN = 6, 'postcode sector mean, (mainly PO Boxes)'
        TERMINATED = 8, 'postcode terminated prior to Gridlink® initiative, last known ONS postcode grid reference'
        NOT_AVAILABLE = 9, 'no grid reference available'

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
