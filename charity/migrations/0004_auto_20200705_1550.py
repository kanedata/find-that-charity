# Generated by Django 3.0.6 on 2020-07-05 14:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("charity", "0003_auto_20200626_1537"),
    ]

    operations = [
        migrations.CreateModel(
            name="CCEWCharity",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("regno", models.CharField(db_index=True, max_length=255)),
                ("subno", models.IntegerField(db_index=True)),
                ("name", models.CharField(max_length=255)),
                ("orgtype", models.CharField(max_length=255)),
                ("gd", models.CharField(max_length=255)),
                ("aob", models.CharField(max_length=255)),
                ("aob_defined", models.CharField(max_length=255)),
                ("nhs", models.CharField(max_length=255)),
                ("ha_no", models.CharField(max_length=255)),
                ("corr", models.CharField(max_length=255)),
                ("add1", models.CharField(max_length=255)),
                ("add2", models.CharField(max_length=255)),
                ("add3", models.CharField(max_length=255)),
                ("add4", models.CharField(max_length=255)),
                ("add5", models.CharField(max_length=255)),
                ("postcode", models.CharField(max_length=255)),
                ("phone", models.CharField(max_length=255)),
                ("fax", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="CCEWCharityAOO",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("regno", models.CharField(db_index=True, max_length=255)),
                ("aootype", models.CharField(max_length=255)),
                ("aookey", models.IntegerField()),
                ("welsh", models.CharField(max_length=255)),
                ("master", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="CCEWClass",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("regno", models.CharField(db_index=True, max_length=255)),
                ("classification", models.CharField(db_column="class", max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="CCEWFinancial",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("regno", models.CharField(db_index=True, max_length=255)),
                ("fystart", models.DateField()),
                ("fyend", models.DateField(db_index=True)),
                ("income", models.BigIntegerField()),
                ("expend", models.BigIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="CCEWMainCharity",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("regno", models.CharField(db_index=True, max_length=255)),
                ("coyno", models.CharField(max_length=255)),
                ("trustees", models.CharField(max_length=255)),
                ("fyend", models.CharField(max_length=255)),
                ("welsh", models.CharField(max_length=255)),
                ("incomedate", models.DateField()),
                ("income", models.BigIntegerField()),
                ("grouptype", models.CharField(max_length=255)),
                ("email", models.CharField(max_length=255)),
                ("web", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="CCEWName",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("regno", models.CharField(db_index=True, max_length=255)),
                ("subno", models.IntegerField(db_index=True)),
                ("nameno", models.IntegerField()),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="CCEWObjects",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("regno", models.CharField(db_index=True, max_length=255)),
                ("subno", models.IntegerField(db_index=True)),
                ("seqno", models.CharField(db_index=True, max_length=255)),
                ("object_text", models.CharField(db_column="object", max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="CCEWPartB",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("regno", models.CharField(db_index=True, max_length=255)),
                ("artype", models.CharField(max_length=255)),
                ("fystart", models.DateField()),
                ("fyend", models.DateField(db_index=True)),
                ("inc_leg", models.BigIntegerField()),
                ("inc_end", models.BigIntegerField()),
                ("inc_vol", models.BigIntegerField()),
                ("inc_fr", models.BigIntegerField()),
                ("inc_char", models.BigIntegerField()),
                ("inc_invest", models.BigIntegerField()),
                ("inc_other", models.BigIntegerField()),
                ("inc_total", models.BigIntegerField()),
                ("invest_gain", models.BigIntegerField()),
                ("asset_gain", models.BigIntegerField()),
                ("pension_gain", models.BigIntegerField()),
                ("exp_vol", models.BigIntegerField()),
                ("exp_trade", models.BigIntegerField()),
                ("exp_invest", models.BigIntegerField()),
                ("exp_grant", models.BigIntegerField()),
                ("exp_charble", models.BigIntegerField()),
                ("exp_gov", models.BigIntegerField()),
                ("exp_other", models.BigIntegerField()),
                ("exp_total", models.BigIntegerField()),
                ("exp_support", models.BigIntegerField()),
                ("exp_dep", models.BigIntegerField()),
                ("reserves", models.BigIntegerField()),
                ("asset_open", models.BigIntegerField()),
                ("asset_close", models.BigIntegerField()),
                ("fixed_assets", models.BigIntegerField()),
                ("open_assets", models.BigIntegerField()),
                ("invest_assets", models.BigIntegerField()),
                ("cash_assets", models.BigIntegerField()),
                ("current_assets", models.BigIntegerField()),
                ("credit_1", models.BigIntegerField()),
                ("credit_long", models.BigIntegerField()),
                ("pension_assets", models.BigIntegerField()),
                ("total_assets", models.BigIntegerField()),
                ("funds_end", models.BigIntegerField()),
                ("funds_restrict", models.BigIntegerField()),
                ("funds_unrestrict", models.BigIntegerField()),
                ("funds_total", models.BigIntegerField()),
                ("employees", models.BigIntegerField()),
                ("volunteers", models.BigIntegerField()),
                ("cons_acc", models.CharField(max_length=255)),
                ("charity_acc", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="CCEWRegistration",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("regno", models.CharField(db_index=True, max_length=255)),
                ("subno", models.IntegerField(db_index=True)),
                ("regdate", models.DateField()),
                ("remdate", models.DateField()),
                ("remcode", models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name="charityraw",
            name="org_id",
            field=models.CharField(db_index=True, max_length=200),
        ),
    ]
