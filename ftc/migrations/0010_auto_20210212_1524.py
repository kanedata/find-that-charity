# Generated by Django 3.1.1 on 2021-02-12 15:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ftc", "0009_organisationlocation"),
    ]

    operations = [
        migrations.AlterField(
            model_name="organisationlocation",
            name="geoCodeType",
            field=models.CharField(
                choices=[
                    ("PC", "UK Postcode"),
                    ("ONS", "ONS code"),
                    ("ISO", "ISO3166-1 Country Code"),
                ],
                db_index=True,
                default="ONS",
                max_length=5,
                verbose_name="Geo Code Type",
            ),
        ),
        migrations.AlterField(
            model_name="organisationlocation",
            name="geo_iso",
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=3,
                null=True,
                verbose_name="ISO3166-1 Country Code",
            ),
        ),
    ]