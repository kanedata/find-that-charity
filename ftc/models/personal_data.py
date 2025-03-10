# List of companies or organisations to remove personal data for


from django.db import models


class PersonalData(models.Model):
    org_id = models.CharField(
        db_index=True,
        verbose_name="Organisation Identifier",
        max_length=255,
        primary_key=True,
    )
    notes = models.TextField(
        verbose_name="Notes",
        help_text="Reason for removal of personal data",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Personal Data"
        verbose_name_plural = "Personal Data"

    def __str__(self):
        return self.org_id
