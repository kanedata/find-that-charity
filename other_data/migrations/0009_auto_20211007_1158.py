# Generated by Django 3.2.5 on 2021-10-07 10:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("other_data", "0008_alter_genderpaygap_scrape"),
    ]

    operations = [
        migrations.AddField(
            model_name="genderpaygap",
            name="EmployerId",
            field=models.CharField(db_index=True, default="-", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="genderpaygap",
            name="PostCode",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
