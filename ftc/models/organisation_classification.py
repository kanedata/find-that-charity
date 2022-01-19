from django.db import models

from .orgid import OrgidField


class OrganisationClassification(models.Model):
    org_id = OrgidField(db_index=True, verbose_name="Organisation Identifier")
    vocabulary = models.ForeignKey(
        "VocabularyEntries",
        related_name="organisations",
        on_delete=models.DO_NOTHING,
    )
    spider = models.CharField(max_length=200, db_index=True)
    source = models.ForeignKey(
        "Source",
        related_name="organisation_classifications",
        on_delete=models.DO_NOTHING,
        db_index=True,
    )
    scrape = models.ForeignKey(
        "Scrape",
        related_name="organisation_classifications",
        on_delete=models.DO_NOTHING,
        db_index=True,
    )
