from django.db import models

from ftc.models.orgid import OrgidField

# Data from: https://uk-third-sector-database.github.io/data/


class CIC(models.Model):
    uid = OrgidField(primary_key=True, verbose_name="Organisation Identifier")
    company_number = models.CharField(
        max_length=8,
        null=True,
        blank=True,
        verbose_name="Companies House registration number",
    )
    regy = models.IntegerField(
        null=True, blank=True, verbose_name="Year of incorporation"
    )
    remy = models.IntegerField(
        null=True, blank=True, verbose_name="Year of dissolution"
    )
    beneficiaries = models.TextField(
        null=True,
        blank=True,
        verbose_name="Section A: Who the companyʼs activities will benefit",
    )
    surplus_use = models.TextField(
        null=True,
        blank=True,
        verbose_name="Section B: How any surplus will be used for community benefit",
    )
    activity_1 = models.TextField(
        null=True, blank=True, verbose_name="Section B: Description of activity 1"
    )
    community_benefit_1 = models.TextField(
        null=True,
        blank=True,
        verbose_name="Section B: How each activity benefits the community 1",
    )
    activity_2 = models.TextField(
        null=True, blank=True, verbose_name="Section B: Description of activity 2"
    )
    community_benefit_2 = models.TextField(
        null=True,
        blank=True,
        verbose_name="Section B: How each activity benefits the community 2",
    )
    activity_3 = models.TextField(
        null=True, blank=True, verbose_name="Section B: Description of activity 3"
    )
    community_benefit_3 = models.TextField(
        null=True,
        blank=True,
        verbose_name="Section B: How each activity benefits the community 3",
    )
    activity_4 = models.TextField(
        null=True, blank=True, verbose_name="Section B: Description of activity 4"
    )
    community_benefit_4 = models.TextField(
        null=True,
        blank=True,
        verbose_name="Section B: How each activity benefits the community 4",
    )
    activity_5 = models.TextField(
        null=True, blank=True, verbose_name="Section B: Description of activity 5"
    )
    community_benefit_5 = models.TextField(
        null=True,
        blank=True,
        verbose_name="Section B: How each activity benefits the community 5",
    )
    activity_6 = models.TextField(
        null=True, blank=True, verbose_name="Section B: Description of activity 6"
    )
    community_benefit_6 = models.TextField(
        null=True,
        blank=True,
        verbose_name="Section B: How each activity benefits the community 6",
    )
    activity_7 = models.TextField(
        null=True, blank=True, verbose_name="Section B: Description of activity 7"
    )
    community_benefit_7 = models.TextField(
        null=True,
        blank=True,
        verbose_name="Section B: How each activity benefits the community 7",
    )
    activity_8 = models.TextField(
        null=True, blank=True, verbose_name="Section B: Description of activity 8"
    )
    community_benefit_8 = models.TextField(
        null=True,
        blank=True,
        verbose_name="Section B: How each activity benefits the community 8",
    )
    activity_9 = models.TextField(
        null=True, blank=True, verbose_name="Section B: Description of activity 9"
    )
    community_benefit_9 = models.TextField(
        null=True,
        blank=True,
        verbose_name="Section B: How each activity benefits the community 9",
    )
    activity_10 = models.TextField(
        null=True, blank=True, verbose_name="Section B: Description of activity 10"
    )
    community_benefit_10 = models.TextField(
        null=True,
        blank=True,
        verbose_name="Section B: How each activity benefits the community 10",
    )
    scrape = models.ForeignKey(
        "ftc.Scrape",
        on_delete=models.DO_NOTHING,
    )
    spider = models.CharField(
        max_length=200, db_index=True, default="tscc-cic-36-forms"
    )
    source = models.ForeignKey(
        "ftc.Source",
        related_name="cics",
        on_delete=models.DO_NOTHING,
        db_index=True,
    )
