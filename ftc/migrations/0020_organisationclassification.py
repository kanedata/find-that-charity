# Generated by Django 3.2.5 on 2022-01-18 23:41

import django.db.models.deletion
from django.db import migrations, models

import ftc.models.orgid


class Migration(migrations.Migration):
    dependencies = [
        ("ftc", "0019_vocabulary_vocabularyentries"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrganisationClassification",
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
                (
                    "org_id",
                    ftc.models.orgid.OrgidField(
                        db_index=True,
                        max_length=200,
                        verbose_name="Organisation Identifier",
                    ),
                ),
                ("spider", models.CharField(db_index=True, max_length=200)),
                (
                    "scrape",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="organisation_classifications",
                        to="ftc.scrape",
                    ),
                ),
                (
                    "source",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="organisation_classifications",
                        to="ftc.source",
                    ),
                ),
                (
                    "vocabulary",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="organisations",
                        to="ftc.vocabularyentries",
                    ),
                ),
            ],
        ),
    ]