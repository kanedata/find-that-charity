# Generated by Django 3.2 on 2021-04-19 12:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ftc", "0015_organisationlocation_spider"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="organisationlocation",
            name="organisation",
        ),
    ]