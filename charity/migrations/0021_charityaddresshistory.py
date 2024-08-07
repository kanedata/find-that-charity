# Generated by Django 3.2.13 on 2022-07-11 15:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("charity", "0020_auto_20220701_1213"),
    ]

    operations = [
        migrations.CreateModel(
            name="CharityAddressHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("org_id", models.CharField(db_index=True, max_length=255)),
                ("address_md5", models.TextField(blank=True, db_index=True, null=True)),
                ("address", models.TextField(blank=True, db_index=True, null=True)),
                (
                    "postcode",
                    models.CharField(
                        blank=True, db_index=True, max_length=255, null=True
                    ),
                ),
                ("first_added", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
            options={
                "unique_together": {("org_id", "address_md5")},
            },
        ),
    ]
