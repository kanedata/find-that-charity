# Generated by Django 5.0.4 on 2025-03-10 09:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ftc", "0040_personaldata"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="personaldata",
            options={
                "verbose_name": "Personal Data",
                "verbose_name_plural": "Personal Data",
            },
        ),
        migrations.AddField(
            model_name="personaldata",
            name="notes",
            field=models.TextField(
                blank=True,
                help_text="Reason for removal of personal data",
                null=True,
                verbose_name="Notes",
            ),
        ),
    ]
