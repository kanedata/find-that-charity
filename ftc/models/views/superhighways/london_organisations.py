from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_db_views.db_view import DBView


class SuperhighwaysLondonOrganisations(DBView):
    organisation_id = models.CharField(max_length=255)
    charity_number = models.IntegerField(null=True)
    organisation_name = models.CharField(max_length=255)
    organisation_type = models.CharField(max_length=255)
    company_number = models.CharField(max_length=255, null=True)
    also_known_as = ArrayField(models.CharField(max_length=255), null=True)
    postcode = models.CharField(max_length=255, null=True)
    website = models.CharField(max_length=255, null=True)
    latest_income = models.BigIntegerField(null=True)
    latest_expenditure = models.BigIntegerField(null=True)
    latest_employees = models.BigIntegerField(null=True)
    latest_volunteers = models.BigIntegerField(null=True)
    latest_trustees = models.BigIntegerField(null=True)
    registration_status = models.CharField(max_length=255, null=True)
    reporting_status = models.CharField(max_length=255, null=True)
    date_of_registration = models.DateField(null=True)
    date_of_removal = models.DateField(null=True)
    date_of_extract = models.DateField(null=True)
    hq_la_code = models.CharField(max_length=200, null=True)
    hq_la_name = models.CharField(max_length=255, null=True)
    hq_rgn_code = models.CharField(max_length=200, null=True)
    hq_rgn_name = models.CharField(max_length=255, null=True)
    hq_ctry_code = models.CharField(max_length=200, null=True)
    hq_ctry_name = models.CharField(max_length=255, null=True)
    hq_london = models.BooleanField(null=True)
    hq_ward_code = models.CharField(max_length=200, null=True)
    hq_ward_name = models.CharField(max_length=255, null=True)
    charity_activities = models.TextField(null=True)
    any_london = models.BooleanField(null=True)
    cqc_category = models.CharField(max_length=255, null=True)
    charity_has_land = models.BooleanField(null=True)
    charity_is_cio = models.BooleanField(null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    class Meta:
        managed = False
        db_table = "superhighways_london_organisations"

    view_definition = """
SELECT organisation_id,
    charity_number,
    organisation_name,
    organisation_type,
    company_number,
    also_known_as,
    postcode,
    website,
    latest_income,
    latest_expenditure,
    latest_employees,
    latest_volunteers,
    latest_trustees,
    registration_status,
    reporting_status,
    date_of_registration,
    date_of_removal,
    date_of_extract,
    hq_la_code,
    hq_la_name,
    hq_rgn_code,
    hq_rgn_name,
    hq_ctry_code,
    hq_ctry_name,
    hq_london,
    hq_ward_code,
    hq_ward_name,
    charity_activities,
    any_london,
    cqc_category,
    charity_has_land,
    charity_is_cio,
    latitude,
    longitude
FROM superhighways_london_organisations_view
"""
