from django.db import models

from .orgid import OrgidField


class OrganisationLink(models.Model):
    org_id_a = OrgidField(max_length=255, db_index=True)
    org_id_b = OrgidField(max_length=255, db_index=True)
    spider = models.CharField(max_length=200, db_index=True)
    source = models.ForeignKey(
        "Source",
        related_name="organisation_links",
        on_delete=models.CASCADE,
    )
    scrape = models.ForeignKey(
        "Scrape",
        related_name="organisation_links",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "From {} to {}".format(self.org_id_a, self.org_id_b)
