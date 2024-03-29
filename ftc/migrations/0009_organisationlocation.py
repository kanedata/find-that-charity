# Generated by Django 3.1.1 on 2021-02-12 14:41

import django.db.models.deletion
from django.db import migrations, models

import ftc.models.orgid


class Migration(migrations.Migration):
    dependencies = [
        ("ftc", "0008_auto_20201002_1408"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrganisationLocation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "org_id",
                    ftc.models.orgid.OrgidField(
                        db_index=True,
                        max_length=200,
                        verbose_name="Organisation Identifier",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Name")),
                (
                    "description",
                    models.TextField(blank=True, null=True, verbose_name="Description"),
                ),
                (
                    "geoCode",
                    models.CharField(
                        blank=True, max_length=200, null=True, verbose_name="Geo Code"
                    ),
                ),
                (
                    "geoCodeType",
                    models.CharField(
                        choices=[
                            ("PC", "Postcode"),
                            ("ONS", "ONS code"),
                            ("ISO", "ISO Country Code"),
                        ],
                        db_index=True,
                        default="ONS",
                        max_length=5,
                        verbose_name="Geo Code Type",
                    ),
                ),
                (
                    "locationType",
                    models.CharField(
                        choices=[
                            ("HQ", "Registered Office"),
                            ("AOO", "Area of operation"),
                            ("SITE", "Site"),
                        ],
                        db_index=True,
                        default="HQ",
                        max_length=5,
                        verbose_name="Location Type",
                    ),
                ),
                (
                    "geo_iso",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        max_length=3,
                        null=True,
                        verbose_name="ISO Country Code",
                    ),
                ),
                (
                    "geo_oa11",
                    models.CharField(
                        blank=True, max_length=9, null=True, verbose_name="Output Area"
                    ),
                ),
                (
                    "geo_cty",
                    models.CharField(
                        blank=True, max_length=9, null=True, verbose_name="County"
                    ),
                ),
                (
                    "geo_laua",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        max_length=9,
                        null=True,
                        verbose_name="Local Authority",
                    ),
                ),
                (
                    "geo_ward",
                    models.CharField(
                        blank=True, max_length=9, null=True, verbose_name="Ward"
                    ),
                ),
                (
                    "geo_ctry",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        max_length=9,
                        null=True,
                        verbose_name="Country",
                    ),
                ),
                (
                    "geo_rgn",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        max_length=9,
                        null=True,
                        verbose_name="Region",
                    ),
                ),
                (
                    "geo_pcon",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        max_length=9,
                        null=True,
                        verbose_name="Parliamentary Constituency",
                    ),
                ),
                (
                    "geo_ttwa",
                    models.CharField(
                        blank=True,
                        max_length=9,
                        null=True,
                        verbose_name="Travel to Work Area",
                    ),
                ),
                (
                    "geo_lsoa11",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        max_length=9,
                        null=True,
                        verbose_name="Lower Super Output Area",
                    ),
                ),
                (
                    "geo_msoa11",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        max_length=9,
                        null=True,
                        verbose_name="Middle Super Output Area",
                    ),
                ),
                (
                    "geo_lep1",
                    models.CharField(
                        blank=True,
                        max_length=9,
                        null=True,
                        verbose_name="Local Enterprise Partnership 1",
                    ),
                ),
                (
                    "geo_lep2",
                    models.CharField(
                        blank=True,
                        max_length=9,
                        null=True,
                        verbose_name="Local Enterprise Partnership 2",
                    ),
                ),
                (
                    "geo_lat",
                    models.FloatField(blank=True, null=True, verbose_name="Latitude"),
                ),
                (
                    "geo_long",
                    models.FloatField(blank=True, null=True, verbose_name="Longitude"),
                ),
                (
                    "organisation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="locations",
                        to="ftc.organisation",
                    ),
                ),
                (
                    "source",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="organisation_locations",
                        to="ftc.source",
                    ),
                ),
            ],
        ),
    ]
