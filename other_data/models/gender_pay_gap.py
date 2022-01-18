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
