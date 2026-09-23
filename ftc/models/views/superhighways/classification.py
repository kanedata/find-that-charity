from django.db import models
from django_db_views.db_view import DBView


class SuperhighwaysClassification(DBView):
    organisation_id = models.CharField(max_length=255)
    charity_number = models.IntegerField(null=True)
    company_number = models.IntegerField(null=True)
    vocabulary = models.CharField(max_length=255)
    category_code = models.CharField(max_length=255)
    category_name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "superhighways_classification"

    view_definition = """
SELECT oc.org_id AS organisation_id,
    CASE
        WHEN oc.org_id::text ~~* 'GB-CHC-%%'::text THEN replace(oc.org_id::text, 'GB-CHC-'::text, ''::text)::integer
        ELSE NULL::integer
    END AS charity_number,
    CASE
        WHEN oc.org_id::text ~~* 'GB-COH-%%'::text THEN replace(oc.org_id::text, 'GB-COH-'::text, ''::text)
        ELSE NULL::text
    END AS company_number,
    v.title AS vocabulary,
    ve.code AS category_code,
    ve.title AS category_name
FROM ftc_vocabulary v
    JOIN ftc_vocabularyentries ve ON v.id = ve.vocabulary_id
    JOIN ftc_organisationclassification oc ON ve.id = oc.vocabulary_id
    JOIN superhighways_london_organisations slo ON slo.organisation_id = oc.org_id
ORDER BY oc.org_id, v.title, ve.code
"""
