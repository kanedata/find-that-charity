# Generated by Django 5.0.4 on 2024-07-12 13:36

import django.contrib.postgres.indexes
import django_better_admin_arrayfield.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ftc", "0031_alter_organisation_parent"),
    ]

    operations = [
        migrations.AddField(
            model_name="organisation",
            name="linked_orgs_official",
            field=django_better_admin_arrayfield.models.fields.ArrayField(
                base_field=models.CharField(blank=True, max_length=200),
                blank=True,
                null=True,
                size=None,
                verbose_name="Linked organisations (official sources)",
            ),
        ),
        migrations.AddIndex(
            model_name="organisation",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["linked_orgs_official"], name="ftc_organis_linked__bff241_gin"
            ),
        ),
    ]