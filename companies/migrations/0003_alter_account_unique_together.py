# Generated by Django 3.2.11 on 2022-01-20 13:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("companies", "0002_auto_20220120_1255"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="account",
            unique_together={("org_id", "financial_year_end")},
        ),
    ]