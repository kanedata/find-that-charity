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

    class Meta:
        managed = False
