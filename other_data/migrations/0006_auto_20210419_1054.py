# Generated by Django 3.2 on 2021-04-19 09:54

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("other_data", "0005_auto_20210419_1019"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cqclocation",
            name="classification",
        ),
        migrations.RemoveField(
            model_name="cqclocation",
            name="provider",
        ),
        migrations.RemoveField(
            model_name="cqclocation",
            name="scrape",
        ),
        migrations.RemoveField(
            model_name="cqcprovider",
            name="brand",
        ),
        migrations.RemoveField(
            model_name="cqcprovider",
            name="scrape",
        ),
        migrations.DeleteModel(
            name="CQCBrand",
        ),
        migrations.DeleteModel(
            name="CQCLocation",
        ),
        migrations.DeleteModel(
            name="CQCProvider",
        ),
    ]
