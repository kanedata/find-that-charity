from django.contrib.postgres.fields import ArrayField
from django.db import models


class DataSources(models.TextChoices):
    CCEW = "ccew", "Charity Commission for England and Wales"


class CharityData(models.Model):
    id = models.IntegerField(primary_key=True)
    source = models.CharField(
        max_length=255, choices=DataSources.choices, default=DataSources.CCEW
    )
    active = models.BooleanField(default=True)
    data = models.JSONField()
    areas_list = ArrayField(models.TextField(blank=True))
    causes_list = ArrayField(models.TextField(blank=True))
    beneficiaries_list = ArrayField(models.TextField(blank=True))
    operations_list = ArrayField(models.TextField(blank=True))
    trustees_list = ArrayField(models.TextField(blank=True))
    funders_list = ArrayField(models.TextField(blank=True))
    registration_date = models.DateField(null=True)
    social_twitter = models.BooleanField(null=True)
    social_facebook = models.BooleanField(null=True)
    region_code = models.CharField(max_length=9, null=True)
    country_code = models.CharField(max_length=9, null=True)
    laua_code = models.CharField(max_length=9, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    class Meta:
        managed = False
