# Generated by Django 3.1.1 on 2020-10-02 13:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ftc", "0007_auto_20201001_1656"),
    ]

    operations = [
        migrations.AddField(
            model_name="organisation",
            name="geo_ctry",
            field=models.CharField(blank=True, db_index=True, max_length=9, null=True),
        ),
        migrations.AddField(
            model_name="organisation",
            name="geo_cty",
            field=models.CharField(blank=True, max_length=9, null=True),
        ),
        migrations.AddField(
            model_name="organisation",
            name="geo_lat",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="organisation",
            name="geo_laua",
            field=models.CharField(blank=True, db_index=True, max_length=9, null=True),
        ),
        migrations.AddField(
            model_name="organisation",
            name="geo_lep1",
            field=models.CharField(blank=True, max_length=9, null=True),
        ),
        migrations.AddField(
            model_name="organisation",
            name="geo_lep2",
            field=models.CharField(blank=True, max_length=9, null=True),
        ),
        migrations.AddField(
            model_name="organisation",
            name="geo_long",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="organisation",
            name="geo_lsoa11",
            field=models.CharField(blank=True, db_index=True, max_length=9, null=True),
        ),
        migrations.AddField(
            model_name="organisation",
            name="geo_msoa11",
            field=models.CharField(blank=True, db_index=True, max_length=9, null=True),
        ),
        migrations.AddField(
            model_name="organisation",
            name="geo_oa11",
            field=models.CharField(blank=True, max_length=9, null=True),
        ),
        migrations.AddField(
            model_name="organisation",
            name="geo_pcon",
            field=models.CharField(blank=True, db_index=True, max_length=9, null=True),
        ),
        migrations.AddField(
            model_name="organisation",
            name="geo_rgn",
            field=models.CharField(blank=True, db_index=True, max_length=9, null=True),
        ),
        migrations.AddField(
            model_name="organisation",
            name="geo_ttwa",
            field=models.CharField(blank=True, max_length=9, null=True),
        ),
        migrations.AddField(
            model_name="organisation",
            name="geo_ward",
            field=models.CharField(blank=True, max_length=9, null=True),
        ),
    ]
