from dateutil.relativedelta import relativedelta
from django.db import models

from ftc.models import OrgidField


class Grant(models.Model):
    class RecipientType(models.TextChoices):
        ORGANISATION = "Organisation"
        INDIVIDUAL = "Individual"

    grant_id = models.CharField(db_index=True, max_length=255)
    title = models.TextField()
    description = models.TextField()
    currency = models.CharField(db_index=True, max_length=255)
    amountAwarded = models.FloatField(db_index=True)
    awardDate = models.DateField(db_index=True)
    plannedDates_duration = models.IntegerField(db_index=True, null=True, blank=True)
    plannedDates_startDate = models.DateField(db_index=True, null=True, blank=True)
    plannedDates_endDate = models.DateField(db_index=True, null=True, blank=True)
    recipientOrganization_id = OrgidField(
        db_index=True, max_length=255, null=True, blank=True
    )
    recipientOrganization_name = models.CharField(
        db_index=True, max_length=255, null=True, blank=True
    )
    recipientOrganization_canonical_id = OrgidField(
        db_index=True,
        max_length=255,
        null=True,
        blank=True,
        help_text="DEPRECATED - do not use this field",
    )
    recipientOrganization_canonical_name = models.CharField(
        db_index=True,
        max_length=255,
        null=True,
        blank=True,
        help_text="DEPRECATED - do not use this field",
    )
    recipientIndividual_id = models.CharField(
        db_index=True, max_length=255, null=True, blank=True
    )
    recipientIndividual_name = models.CharField(
        db_index=True, max_length=255, null=True, blank=True
    )
    recipient_type = models.CharField(
        db_index=True,
        max_length=255,
        choices=RecipientType.choices,
        default=RecipientType.ORGANISATION,
    )
    fundingOrganization_id = OrgidField(db_index=True, max_length=255)
    fundingOrganization_name = models.CharField(db_index=True, max_length=255)
    fundingOrganization_canonical_id = OrgidField(
        db_index=True,
        max_length=255,
        null=True,
        blank=True,
        help_text="DEPRECATED - do not use this field",
    )
    fundingOrganization_canonical_name = models.CharField(
        db_index=True,
        max_length=255,
        null=True,
        blank=True,
        help_text="DEPRECATED - do not use this field",
    )
    fundingOrganization_type = models.CharField(
        db_index=True, max_length=255, null=True, blank=True
    )
    grantProgramme_title = models.CharField(
        db_index=True, max_length=255, null=True, blank=True
    )
    publisher_prefix = models.CharField(db_index=True, max_length=255)
    publisher_name = models.CharField(db_index=True, max_length=255)
    license = models.CharField(db_index=True, max_length=255)
    scrape = models.ForeignKey(
        "ftc.Scrape",
        on_delete=models.DO_NOTHING,
    )
    spider = models.CharField(max_length=200, db_index=True, default="360g")

    def __str__(self):
        return "<Grant from {} to {}>".format(
            self.fundingOrganization_name,
            self.recipientOrganization_name
            if self.recipientOrganization_name
            else self.recipientIndividual_name,
        )

    @property
    def start_end(self):
        s = ""
        if self.plannedDates_startDate and self.plannedDates_endDate:
            start = self.plannedDates_startDate.strftime("%b %Y")
            end = self.plannedDates_endDate.strftime("%b %Y")
            if start == end:
                s += start
            else:
                s += "{} to {}".format(start, end)
        elif self.plannedDates_startDate and self.plannedDates_duration:
            start = self.plannedDates_startDate.strftime("%b %Y")
            end = self.plannedDates_startDate + relativedelta(
                months=self.plannedDates_duration
            )
            end = end.strftime("%b %Y")
            s += "{} to {}".format(start, end)
        elif self.plannedDates_endDate and self.plannedDates_duration:
            end = self.plannedDates_endDate.strftime("%b %Y")
            start = self.plannedDates_endDate - relativedelta(
                months=self.plannedDates_duration
            )
            start = start.strftime("%b %Y")
            s += "{} to {}".format(start, end)
        return s

    @property
    def duration(self):
        s = ""
        months = None
        if self.plannedDates_startDate and self.plannedDates_endDate:
            start = self.plannedDates_startDate.strftime("%b %Y")
            end = self.plannedDates_endDate.strftime("%b %Y")
            days = (self.plannedDates_endDate - self.plannedDates_startDate).days
            # work out duration in months
            months = days / 30.5
            if start == end:
                s += start
            else:
                s += "{} to {}".format(start, end)
        if self.plannedDates_duration:
            months = self.plannedDates_duration
        if months:
            if months >= 12:
                years = int(months / 12)
                months = int(months % 12)
                month_str = "{} {}".format(
                    years,
                    "year" if years == 1 else "years",
                )
            else:
                month_str = "{} {}".format(
                    months,
                    "month" if months == 1 else "months",
                )
            return month_str
        return s
