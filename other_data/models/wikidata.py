from django.db import models

from ftc.models import OrgidField


class WikiDataItem(models.Model):
    org_id = OrgidField(
        db_index=True, verbose_name="Organisation Identifier", null=True, blank=True
    )
    wikidata_id = models.CharField(db_index=True, max_length=255)
    wikipedia_url = models.URLField(null=True, blank=True, max_length=1000)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    facebook = models.CharField(max_length=255, null=True, blank=True)
    grid_id = models.CharField(max_length=255, null=True, blank=True)
    scrape = models.ForeignKey(
        "ftc.Scrape",
        on_delete=models.DO_NOTHING,
    )
    spider = models.CharField(max_length=200, db_index=True, default="wd")

    def __str__(self):
        return self.wikidata_id
