# Generated by Django 3.2 on 2021-04-17 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("charity", "0011_auto_20210417_1040"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ccewcharityareaofoperation",
            name="geographic_area_description",
            field=models.CharField(
                blank=True, db_index=True, max_length=255, null=True
            ),
        ),
    ]