# Generated by Django 3.1.1 on 2020-10-19 23:37

import django.db.models.deletion
import django_better_admin_arrayfield.models.fields
from django.db import migrations, models

import ftc.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("ftc", "0008_auto_20201002_1408"),
    ]

    operations = [
        migrations.CreateModel(
            name="GenderPayGap",
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
                    ftc.models.OrgidField(
                        blank=True,
                        db_index=True,
                        max_length=200,
                        null=True,
                        verbose_name="Organisation Identifier",
                    ),
                ),
                ("Year", models.IntegerField(db_index=True)),
                ("EmployerName", models.CharField(db_index=True, max_length=255)),
                ("Address", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "CompanyNumber",
                    models.CharField(
                        blank=True, db_index=True, max_length=255, null=True
                    ),
                ),
                (
                    "SicCodes",
                    django_better_admin_arrayfield.models.fields.ArrayField(
                        base_field=models.CharField(max_length=100),
                        blank=True,
                        null=True,
                        size=None,
                    ),
                ),
                ("DiffMeanHourlyPercent", models.FloatField(blank=True, null=True)),
                ("DiffMedianHourlyPercent", models.FloatField(blank=True, null=True)),
                ("DiffMeanBonusPercent", models.FloatField(blank=True, null=True)),
                ("DiffMedianBonusPercent", models.FloatField(blank=True, null=True)),
                ("MaleBonusPercent", models.FloatField(blank=True, null=True)),
                ("FemaleBonusPercent", models.FloatField(blank=True, null=True)),
                ("MaleLowerQuartile", models.FloatField(blank=True, null=True)),
                ("FemaleLowerQuartile", models.FloatField(blank=True, null=True)),
                ("MaleLowerMiddleQuartile", models.FloatField(blank=True, null=True)),
                ("FemaleLowerMiddleQuartile", models.FloatField(blank=True, null=True)),
                ("MaleUpperMiddleQuartile", models.FloatField(blank=True, null=True)),
                ("FemaleUpperMiddleQuartile", models.FloatField(blank=True, null=True)),
                ("MaleTopQuartile", models.FloatField(blank=True, null=True)),
                ("FemaleTopQuartile", models.FloatField(blank=True, null=True)),
                (
                    "CompanyLinkToGPGInfo",
                    models.URLField(blank=True, max_length=1000, null=True),
                ),
                (
                    "ResponsiblePerson",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "EmployerSize",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Less than 250", "Less Than 250"),
                            ("250 to 499", "From 250 To 499"),
                            ("500 to 999", "From 500 To 999"),
                            ("1000 to 4999", "From 1000 To 4999"),
                            ("5000 to 19,999", "From 5000 To 19999"),
                        ],
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "CurrentName",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "SubmittedAfterTheDeadline",
                    models.BooleanField(blank=True, null=True),
                ),
                ("DueDate", models.DateField(blank=True, null=True)),
                ("DateSubmitted", models.DateField(blank=True, null=True)),
                (
                    "scrape",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="ftc.scrape"
                    ),
                ),
            ],
        ),
    ]
