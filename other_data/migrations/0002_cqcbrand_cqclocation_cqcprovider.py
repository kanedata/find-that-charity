# Generated by Django 3.1.1 on 2020-10-19 23:37

import django.db.models.deletion
from django.db import migrations, models

import ftc.models


class Migration(migrations.Migration):
    dependencies = [
        ("charity", "0009_auto_20200921_1156"),
        ("ftc", "0008_auto_20201002_1408"),
        ("other_data", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CQCBrand",
            fields=[
                (
                    "id",
                    models.CharField(
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                        verbose_name="Brand ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Brand Name")),
                (
                    "scrape",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="ftc.scrape"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CQCProvider",
            fields=[
                (
                    "company_number",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Provider Companies House Number",
                    ),
                ),
                (
                    "charity_number",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Provider Charity Number",
                    ),
                ),
                (
                    "org_id",
                    ftc.models.OrgidField(
                        blank=True,
                        db_index=True,
                        max_length=200,
                        null=True,
                        verbose_name="Organisation Identifier",
                    ),
                ),
                (
                    "id",
                    models.CharField(
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                        verbose_name="Provider ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=255, verbose_name="Provider Name"),
                ),
                (
                    "start_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="Provider HSCA start date"
                    ),
                ),
                (
                    "end_date",
                    models.DateField(
                        blank=True,
                        default=None,
                        null=True,
                        verbose_name="Provider HSCA end date",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Registered", "Registered"),
                            ("Deregistered (E)", "Deregistered E"),
                            ("Deregistered (V)", "Deregistered V"),
                            ("Dissolved", "Dissolved"),
                            ("Removed", "Removed"),
                        ],
                        default="Registered",
                        max_length=255,
                        null=True,
                        verbose_name="Provider Status",
                    ),
                ),
                (
                    "sector",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Social Care Org", "Social Care"),
                            ("Independent Healthcare Org", "Independent Healthcare"),
                            ("Primary Dental Care", "Primary Dental Care"),
                            ("Primary Medical Services", "Primary Medical Services"),
                            ("Independent Ambulance", "Independent Ambulance"),
                            (
                                "NHS Healthcare Organisation",
                                "Nhs Healthcase Organisation",
                            ),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="Provider Type/Sector",
                    ),
                ),
                (
                    "directorate",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Adult social care", "Adult Social Care"),
                            ("Hospitals", "Hospitals"),
                            ("Primary medical services", "Primary Medical Services"),
                            ("Unspecified", "Unspecified"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="Provider Inspection Directorate",
                    ),
                ),
                (
                    "inspection_category",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Provider Primary Inspection Category",
                    ),
                ),
                (
                    "ownership_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Organisation", "Organisation"),
                            ("Individual", "Individual"),
                            ("Partnership", "Partnership"),
                            ("NHS Body", "Nhs Body"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="Provider Ownership Type",
                    ),
                ),
                (
                    "telephone",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Provider Telephone Number",
                    ),
                ),
                (
                    "web",
                    models.URLField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Provider Web Address",
                    ),
                ),
                (
                    "address_street",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Provider Street Address",
                    ),
                ),
                (
                    "address_2",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Provider Address Line 2",
                    ),
                ),
                (
                    "address_city",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Provider City",
                    ),
                ),
                (
                    "address_county",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Provider County",
                    ),
                ),
                (
                    "address_postcode",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Provider Postal Code",
                    ),
                ),
                (
                    "geo_uprn",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Provider PAF / UPRN ID",
                    ),
                ),
                (
                    "geo_local_authority",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Provider Local Authority",
                    ),
                ),
                (
                    "geo_region",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Provider Region",
                    ),
                ),
                (
                    "geo_latitude",
                    models.FloatField(
                        blank=True, null=True, verbose_name="Provider Latitude"
                    ),
                ),
                (
                    "geo_longitude",
                    models.FloatField(
                        blank=True, null=True, verbose_name="Provider Longitude"
                    ),
                ),
                (
                    "geo_pcon",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Provider Parliamentary Constituency",
                    ),
                ),
                (
                    "brand",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="other_data.cqcbrand",
                    ),
                ),
                (
                    "scrape",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="ftc.scrape"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CQCLocation",
            fields=[
                (
                    "id",
                    models.CharField(
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                        verbose_name="Location ID",
                    ),
                ),
                (
                    "start_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="Location HSCA start date"
                    ),
                ),
                (
                    "end_date",
                    models.DateField(
                        blank=True,
                        default=None,
                        null=True,
                        verbose_name="Location HSCA end date",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Active", "Active"),
                            ("Inactive-Dereg", "Inactive"),
                            ("Removed", "Removed"),
                        ],
                        default="Active",
                        max_length=255,
                        null=True,
                        verbose_name="Location Status",
                    ),
                ),
                (
                    "care_home",
                    models.BooleanField(
                        blank=True, null=True, verbose_name="Care home?"
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=255, verbose_name="Location Name"),
                ),
                (
                    "ods_code",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Location ODS Code",
                    ),
                ),
                (
                    "telephone",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Location Telephone Number",
                    ),
                ),
                (
                    "web",
                    models.URLField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Location Web Address",
                    ),
                ),
                (
                    "care_home_beds",
                    models.IntegerField(
                        blank=True, null=True, verbose_name="Care homes beds"
                    ),
                ),
                (
                    "sector",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Social Care Org", "Social Care"),
                            ("Independent Healthcare Org", "Independent Healthcare"),
                            ("Primary Dental Care", "Primary Dental Care"),
                            ("Primary Medical Services", "Primary Medical Services"),
                            ("Independent Ambulance", "Independent Ambulance"),
                            (
                                "NHS Healthcare Organisation",
                                "Nhs Healthcase Organisation",
                            ),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="Location Type/Sector",
                    ),
                ),
                (
                    "directorate",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Adult social care", "Adult Social Care"),
                            ("Hospitals", "Hospitals"),
                            ("Primary medical services", "Primary Medical Services"),
                            ("Unspecified", "Unspecified"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="Location Inspection Directorate",
                    ),
                ),
                (
                    "inspection_category",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Location Primary Inspection Category",
                    ),
                ),
                (
                    "latest_overall_rating",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Inadequate", "Inadequate"),
                            ("Requires improvement", "Requires Improvement"),
                            ("Good", "Good"),
                            ("Outstanding", "Outstanding"),
                        ],
                        max_length=255,
                        null=True,
                        verbose_name="Location Latest Overall Rating",
                    ),
                ),
                (
                    "publication_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="Publication Date"
                    ),
                ),
                (
                    "inherited_rating",
                    models.BooleanField(
                        blank=True, null=True, verbose_name="Inherited Rating (Y/N)"
                    ),
                ),
                (
                    "geo_region",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Location Region",
                    ),
                ),
                (
                    "geo_local_authority",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Location Local Authority",
                    ),
                ),
                (
                    "geo_onspd_ccg_code",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Location ONSPD CCG Code",
                    ),
                ),
                (
                    "geo_onspd_ccg",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Location ONSPD CCG",
                    ),
                ),
                (
                    "geo_commissioning_ccg_code",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Location Commissioning CCG Code",
                    ),
                ),
                (
                    "geo_commissioning_ccg",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Location Commissioning CCG",
                    ),
                ),
                (
                    "address_street",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Location Street Address",
                    ),
                ),
                (
                    "address_2",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Location Address Line 2",
                    ),
                ),
                (
                    "address_city",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Location City",
                    ),
                ),
                (
                    "address_county",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Location County",
                    ),
                ),
                (
                    "address_postcode",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Location Postal Code",
                    ),
                ),
                (
                    "geo_uprn",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Location PAF / UPRN ID",
                    ),
                ),
                (
                    "geo_latitude",
                    models.FloatField(
                        blank=True, null=True, verbose_name="Location Latitude"
                    ),
                ),
                (
                    "geo_longitude",
                    models.FloatField(
                        blank=True, null=True, verbose_name="Location Longitude"
                    ),
                ),
                (
                    "geo_pcon",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Location Parliamentary Constituency",
                    ),
                ),
                (
                    "classification",
                    models.ManyToManyField(to="charity.VocabularyEntries"),
                ),
                (
                    "provider",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="locations",
                        to="other_data.cqcprovider",
                    ),
                ),
                (
                    "scrape",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="ftc.scrape"
                    ),
                ),
            ],
        ),
    ]
