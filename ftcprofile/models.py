from django.conf import settings
from django.db import models


# Create your models here.
class OrganisationTag(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name="tagged_organisations",
    )
    org_id = models.CharField(max_length=100)
    tag = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "org_id", "tag")

    def __str__(self):
        return f"{self.user} tagged {self.org_id} with {self.tag}"
