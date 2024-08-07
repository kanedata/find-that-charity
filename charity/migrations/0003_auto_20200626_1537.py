# Generated by Django 3.0.6 on 2020-06-26 14:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("charity", "0002_ccewdatafile"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="areaofoperation",
            options={
                "verbose_name": "Area of operation",
                "verbose_name_plural": "Areas of operation",
            },
        ),
        migrations.AlterModelOptions(
            name="ccewdatafile",
            options={
                "verbose_name": "Charity Commission data file",
                "verbose_name_plural": "Charity Commission data files",
            },
        ),
        migrations.AlterModelOptions(
            name="charity",
            options={"verbose_name_plural": "Charities"},
        ),
        migrations.AlterModelOptions(
            name="charityraw",
            options={
                "verbose_name": "Raw charity data",
                "verbose_name_plural": "Raw charity data",
            },
        ),
        migrations.AlterModelOptions(
            name="vocabulary",
            options={
                "verbose_name": "Vocabulary",
                "verbose_name_plural": "Vocabularies",
            },
        ),
        migrations.AlterModelOptions(
            name="vocabularyentries",
            options={
                "verbose_name": "Vocabulary Entry",
                "verbose_name_plural": "Vocabulary Entries",
            },
        ),
        migrations.AlterField(
            model_name="areaofoperation",
            name="ContinentCode",
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=2,
                null=True,
                verbose_name="Continent",
            ),
        ),
    ]
