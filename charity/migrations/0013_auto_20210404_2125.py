# Generated by Django 3.1.1 on 2021-04-04 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("charity", "0012_auto_20210403_1943"),
    ]

    operations = [
        migrations.AlterField(
            model_name="areaofoperation",
            name="aookey",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="areaofoperation",
            name="aootype",
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name="areaofoperation",
            name="welsh",
            field=models.BooleanField(blank=True, null=True, verbose_name="In Wales"),
        ),
        migrations.AlterUniqueTogether(
            name="areaofoperation",
            unique_together=set(),
        ),
    ]