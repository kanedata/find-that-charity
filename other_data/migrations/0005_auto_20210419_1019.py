# Generated by Django 3.2 on 2021-04-19 09:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("other_data", "0004_alter_genderpaygap_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="cqcbrand",
            name="spider",
            field=models.CharField(db_index=True, default="cqc", max_length=200),
        ),
        migrations.AddField(
            model_name="cqclocation",
            name="spider",
            field=models.CharField(db_index=True, default="cqc", max_length=200),
        ),
        migrations.AddField(
            model_name="cqcprovider",
            name="spider",
            field=models.CharField(db_index=True, default="cqc", max_length=200),
        ),
        migrations.AddField(
            model_name="genderpaygap",
            name="spider",
            field=models.CharField(db_index=True, default="gpg", max_length=200),
        ),
    ]