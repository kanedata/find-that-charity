# Generated by Django 3.2.13 on 2022-07-01 11:13

import django.db.models.deletion
from django.db import migrations, models


def set_proper_defaults(apps, schema_editor):
    Charity = apps.get_model("charity", "Charity")
    Scrape = apps.get_model("ftc", "Scrape")
    Charity.objects.update(spider=models.F("source"))

    for spider in Charity.objects.values_list("spider", flat=True).distinct():
        scrape_id = (
            Scrape.objects.filter(status="success", spider=spider)
            .order_by("-finish_time")
            .first()
            .id
        )
        Charity.objects.filter(spider=spider).update(scrape_id=scrape_id)


class Migration(migrations.Migration):

    dependencies = [
        ("ftc", "0026_auto_20220701_1149"),
        ("charity", "0019_auto_20220302_1119"),
    ]

    operations = [
        migrations.AddField(
            model_name="charity",
            name="scrape",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="charities",
                to="ftc.scrape",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="charity",
            name="spider",
            field=models.CharField(db_index=True, default="ccew", max_length=200),
            preserve_default=False,
        ),
        migrations.RunPython(set_proper_defaults, migrations.RunPython.noop),
    ]