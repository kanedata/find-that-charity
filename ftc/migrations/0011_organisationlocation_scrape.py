# Generated by Django 3.1.1 on 2021-02-12 17:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ftc", "0010_auto_20210212_1524"),
    ]

    operations = [
        migrations.AddField(
            model_name="organisationlocation",
            name="scrape",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="organisation_locations",
                to="ftc.scrape",
            ),
            preserve_default=False,
        ),
    ]
