# Generated by Django 3.2.11 on 2022-03-02 11:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("charity", "0018_remove_charity_classification"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ccewcharityannualreturnhistory",
            name="fin_period_end_date",
            field=models.DateField(
                blank=True,
                db_index=True,
                help_text="The end date of the financial period which is detailed for the charity.",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="ccewcharityarpartb",
            name="fin_period_end_date",
            field=models.DateField(
                blank=True,
                db_index=True,
                help_text="The end date of the financial period which is detailed for the charity.",
                null=True,
            ),
        ),
    ]
