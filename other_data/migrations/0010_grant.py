# Generated by Django 3.2.5 on 2022-01-18 15:37

import django.db.models.deletion
from django.db import migrations, models

import ftc.models.orgid


class Migration(migrations.Migration):

    dependencies = [
        ("ftc", "0018_alter_organisationlocation_unique_together"),
        ("other_data", "0009_auto_20211007_1158"),
    ]

    operations = [
        migrations.CreateModel(
            name="Grant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("grant_id", models.CharField(db_index=True, max_length=255)),
                ("title", models.TextField()),
                ("description", models.TextField()),
                ("currency", models.CharField(db_index=True, max_length=255)),
                ("amountAwarded", models.FloatField(db_index=True)),
                ("awardDate", models.DateField(db_index=True)),
                (
                    "recipientOrganization_id",
                    ftc.models.orgid.OrgidField(db_index=True, max_length=200),
                ),
                (
                    "recipientOrganization_name",
                    models.CharField(db_index=True, max_length=255),
                ),
                (
                    "fundingOrganization_id",
                    ftc.models.orgid.OrgidField(db_index=True, max_length=200),
                ),
                (
                    "fundingOrganization_name",
                    models.CharField(db_index=True, max_length=255),
                ),
                ("publisher_prefix", models.CharField(db_index=True, max_length=255)),
                ("publisher_name", models.CharField(db_index=True, max_length=255)),
                ("license", models.CharField(db_index=True, max_length=255)),
                (
                    "spider",
                    models.CharField(db_index=True, default="360g", max_length=200),
                ),
                (
                    "scrape",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING, to="ftc.scrape"
                    ),
                ),
            ],
        ),
    ]