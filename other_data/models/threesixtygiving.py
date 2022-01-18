from django.db import models

from ftc.models import OrgidField


class Grant(models.Model):
    grant_id = models.CharField(db_index=True, max_length=255)
    title = models.TextField()
    description = models.TextField()
    currency = models.CharField(db_index=True, max_length=255)
    amountAwarded = models.FloatField(db_index=True)
    awardDate = models.DateField(db_index=True)
    recipientOrganization_id = OrgidField(db_index=True, max_length=255)
    recipientOrganization_name = models.CharField(db_index=True, max_length=255)
    fundingOrganization_id = OrgidField(db_index=True, max_length=255)
    fundingOrganization_name = models.CharField(db_index=True, max_length=255)
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
            self.fundingOrganization_name, self.recipientOrganization_name
        )
