from django.db import models
from django_db_views.db_view import DBView


class SuperhighwaysTrustees(DBView):
    organisation_id = models.CharField(max_length=255)
    charity_number = models.IntegerField(null=True)
    trustee_id = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = "superhighways_trustees"

    view_definition = """
SELECT 'GB-CHC-'::text || registered_charity_number AS organisation_id,
    registered_charity_number AS charity_number,
    trustee_id
FROM charity_ccewcharitytrustee c
    JOIN superhighways_london_organisations slo ON slo.organisation_id = 'GB-CHC-' || c.registered_charity_number
WHERE linked_charity_number = 0
"""
