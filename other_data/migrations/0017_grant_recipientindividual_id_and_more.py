# Generated by Django 4.1.7 on 2023-05-15 07:56

from django.db import migrations, models

import ftc.models.orgid


class Migration(migrations.Migration):
    dependencies = [
        ("other_data", "0016_grant_fundingorganization_canonical_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="grant",
            name="recipientIndividual_id",
            field=models.CharField(
                blank=True, db_index=True, max_length=255, null=True
            ),
        ),
        migrations.AddField(
            model_name="grant",
            name="recipientIndividual_name",
            field=models.CharField(
                blank=True, db_index=True, max_length=255, null=True
            ),
        ),
        migrations.AddField(
            model_name="grant",
            name="recipient_type",
            field=models.CharField(
                choices=[
                    ("Organisation", "Organisation"),
                    ("Individual", "Individual"),
                ],
                db_index=True,
                default="Organisation",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="grant",
            name="recipientOrganization_canonical_id",
            field=ftc.models.orgid.OrgidField(
                blank=True, db_index=True, max_length=200, null=True
            ),
        ),
        migrations.AlterField(
            model_name="grant",
            name="recipientOrganization_canonical_name",
            field=models.CharField(
                blank=True, db_index=True, max_length=255, null=True
            ),
        ),
        migrations.AlterField(
            model_name="grant",
            name="recipientOrganization_id",
            field=ftc.models.orgid.OrgidField(
                blank=True, db_index=True, max_length=200, null=True
            ),
        ),
        migrations.AlterField(
            model_name="grant",
            name="recipientOrganization_name",
            field=models.CharField(
                blank=True, db_index=True, max_length=255, null=True
            ),
        ),
    ]
