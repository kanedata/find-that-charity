# Generated by Django 3.1.1 on 2021-04-03 18:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("charity", "0010_auto_20210403_1729"),
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
                ("date_of_extract", models.DateField(blank=True, null=True)),
                ("organisation_number", models.IntegerField()),
                ("registered_charity_number", models.IntegerField(db_index=True)),
                ("linked_charity_number", models.IntegerField(db_index=True)),
                (
                    "charity_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "charity_type",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "charity_registration_status",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("date_of_registration", models.DateField(blank=True, null=True)),
                ("date_of_removal", models.DateField(blank=True, null=True)),
                (
                    "charity_reporting_status",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "latest_acc_fin_period_start_date",
                    models.DateField(blank=True, null=True),
                ),
                (
                    "latest_acc_fin_period_end_date",
                    models.DateField(blank=True, null=True),
                ),
                ("latest_income", models.FloatField(blank=True, null=True)),
                ("latest_expenditure", models.FloatField(blank=True, null=True)),
                (
                    "charity_contact_address1",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "charity_contact_address2",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "charity_contact_address3",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "charity_contact_address4",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "charity_contact_address5",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "charity_contact_postcode",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "charity_contact_phone",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "charity_contact_email",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "charity_contact_web",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "charity_company_registration_number",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("charity_insolvent", models.BooleanField(blank=True, null=True)),
                (
                    "charity_in_administration",
                    models.BooleanField(blank=True, null=True),
                ),
                (
                    "charity_previously_excepted",
                    models.BooleanField(blank=True, null=True),
                ),
                (
                    "charity_is_cdf_or_cif",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("charity_is_cio", models.BooleanField(blank=True, null=True)),
                ("cio_is_dissolved", models.BooleanField(blank=True, null=True)),
                (
                    "date_cio_dissolution_notice",
                    models.DateField(blank=True, null=True),
                ),
                ("charity_activities", models.TextField(blank=True, null=True)),
                ("charity_gift_aid", models.BooleanField(blank=True, null=True)),
                ("charity_has_land", models.BooleanField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="CCEWCharityAnnualReturnHistory",
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
                ("date_of_extract", models.DateField(blank=True, null=True)),
                ("organisation_number", models.IntegerField()),
                ("registered_charity_number", models.IntegerField(db_index=True)),
                ("fin_period_start_date", models.DateField(blank=True, null=True)),
                ("fin_period_end_date", models.DateField(blank=True, null=True)),
                (
                    "ar_cycle_reference",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("reporting_due_date", models.DateField(blank=True, null=True)),
                (
                    "date_annual_return_received",
                    models.DateField(blank=True, null=True),
                ),
                ("date_accounts_received", models.DateField(blank=True, null=True)),
                ("total_gross_income", models.BigIntegerField(blank=True, null=True)),
                (
                    "total_gross_expenditure",
                    models.BigIntegerField(blank=True, null=True),
                ),
                ("accounts_qualified", models.BooleanField(blank=True, null=True)),
                ("suppression_ind", models.BooleanField(blank=True, null=True)),
                (
                    "suppression_type",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CCEWCharityAreaOfOperation",
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
                ("date_of_extract", models.DateField(blank=True, null=True)),
                ("organisation_number", models.IntegerField()),
                ("registered_charity_number", models.IntegerField(db_index=True)),
                ("linked_charity_number", models.IntegerField(blank=True, null=True)),
                (
                    "geographic_area_type",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "geographic_area_description",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "parent_geographic_area_type",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "parent_geographic_area_description",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("welsh_ind", models.BooleanField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="CCEWCharityARPartA",
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
                ("date_of_extract", models.DateField(blank=True, null=True)),
                ("organisation_number", models.IntegerField()),
                ("registered_charity_number", models.IntegerField(db_index=True)),
                (
                    "latest_fin_period_submitted_ind",
                    models.BooleanField(blank=True, null=True),
                ),
                ("fin_period_order_number", models.IntegerField(blank=True, null=True)),
                (
                    "ar_cycle_reference",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("fin_period_start_date", models.DateField(blank=True, null=True)),
                ("fin_period_end_date", models.DateField(blank=True, null=True)),
                ("ar_due_date", models.DateField(blank=True, null=True)),
                ("ar_received_date", models.DateField(blank=True, null=True)),
                ("total_gross_income", models.BigIntegerField(blank=True, null=True)),
                (
                    "total_gross_expenditure",
                    models.BigIntegerField(blank=True, null=True),
                ),
                (
                    "charity_raises_funds_from_public",
                    models.BooleanField(blank=True, null=True),
                ),
                (
                    "charity_professional_fundraiser",
                    models.BooleanField(blank=True, null=True),
                ),
                (
                    "charity_agreement_professional_fundraiser",
                    models.BooleanField(blank=True, null=True),
                ),
                (
                    "charity_commercial_participator",
                    models.BooleanField(blank=True, null=True),
                ),
                (
                    "charity_agreement_commerical_participator",
                    models.BooleanField(blank=True, null=True),
                ),
                (
                    "grant_making_is_main_activity",
                    models.BooleanField(blank=True, null=True),
                ),
                (
                    "charity_receives_govt_funding_contracts",
                    models.BooleanField(blank=True, null=True),
                ),
                ("count_govt_contracts", models.IntegerField(blank=True, null=True)),
                (
                    "charity_receives_govt_funding_grants",
                    models.BooleanField(blank=True, null=True),
                ),
                ("count_govt_grants", models.IntegerField(blank=True, null=True)),
                (
                    "income_from_government_contracts",
                    models.BigIntegerField(blank=True, null=True),
                ),
                (
                    "income_from_government_grants",
                    models.BigIntegerField(blank=True, null=True),
                ),
                (
                    "charity_has_trading_subsidiary",
                    models.BooleanField(blank=True, null=True),
                ),
                (
                    "trustee_also_director_of_subsidiary",
                    models.BooleanField(blank=True, null=True),
                ),
                (
                    "does_trustee_receive_any_benefit",
                    models.BooleanField(blank=True, null=True),
                ),
                (
                    "trustee_payments_acting_as_trustee",
                    models.BooleanField(blank=True, null=True),
                ),
                (
                    "trustee_receives_payments_services",
                    models.BooleanField(blank=True, null=True),
                ),
                (
                    "trustee_receives_other_benefit",
                    models.BooleanField(blank=True, null=True),
                ),
                (
                    "trustee_resigned_employment",
                    models.BooleanField(blank=True, null=True),
                ),
                (
                    "employees_salary_over_60k",
                    models.BooleanField(blank=True, null=True),
                ),
                (
                    "count_salary_band_60001_70000",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "count_salary_band_70001_80000",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "count_salary_band_80001_90000",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "count_salary_band_90001_100000",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "count_salary_band_100001_110000",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "count_salary_band_110001_120000",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "count_salary_band_120001_130000",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "count_salary_band_130001_140000",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "count_salary_band_140001_150000",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "count_salary_band_150001_200000",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "count_salary_band_200001_250000",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "count_salary_band_250001_300000",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "count_salary_band_300001_350000",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "count_salary_band_350001_400000",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "count_salary_band_400001_450000",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "count_salary_band_450001_500000",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "count_salary_band_over_500000",
                    models.IntegerField(blank=True, null=True),
                ),
                ("count_volunteers", models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="CCEWCharityARPartB",
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
                ("date_of_extract", models.DateField(blank=True, null=True)),
                ("organisation_number", models.IntegerField()),
                ("registered_charity_number", models.IntegerField(db_index=True)),
                (
                    "latest_fin_period_submitted_ind",
                    models.BooleanField(blank=True, null=True),
                ),
                ("fin_period_order_number", models.IntegerField(blank=True, null=True)),
                ("ar_cycle_reference", models.CharField(max_length=255)),
                ("fin_period_start_date", models.DateField(blank=True, null=True)),
                ("fin_period_end_date", models.DateField(blank=True, null=True)),
                ("ar_due_date", models.DateField(blank=True, null=True)),
                ("ar_received_date", models.DateField(blank=True, null=True)),
                (
                    "income_donations_and_legacies",
                    models.BigIntegerField(blank=True, null=True),
                ),
                (
                    "income_charitable_activities",
                    models.BigIntegerField(blank=True, null=True),
                ),
                (
                    "income_other_trading_activities",
                    models.BigIntegerField(blank=True, null=True),
                ),
                ("income_investments", models.BigIntegerField(blank=True, null=True)),
                ("income_other", models.BigIntegerField(blank=True, null=True)),
                (
                    "income_total_income_and_endowments",
                    models.BigIntegerField(blank=True, null=True),
                ),
                ("income_legacies", models.BigIntegerField(blank=True, null=True)),
                ("income_endowments", models.BigIntegerField(blank=True, null=True)),
                (
                    "expenditure_raising_funds",
                    models.BigIntegerField(blank=True, null=True),
                ),
                (
                    "expenditure_charitable_expenditure",
                    models.BigIntegerField(blank=True, null=True),
                ),
                ("expenditure_other", models.BigIntegerField(blank=True, null=True)),
                ("expenditure_total", models.BigIntegerField(blank=True, null=True)),
                (
                    "expenditure_investment_management",
                    models.BigIntegerField(blank=True, null=True),
                ),
                (
                    "expenditure_grants_institution",
                    models.BigIntegerField(blank=True, null=True),
                ),
                (
                    "expenditure_governance",
                    models.BigIntegerField(blank=True, null=True),
                ),
                (
                    "expenditure_support_costs",
                    models.BigIntegerField(blank=True, null=True),
                ),
                (
                    "expenditure_depreciation",
                    models.BigIntegerField(blank=True, null=True),
                ),
                ("gain_loss_investment", models.BigIntegerField(blank=True, null=True)),
                (
                    "gain_loss_pension_fund",
                    models.BigIntegerField(blank=True, null=True),
                ),
                (
                    "gain_loss_revaluation_fixed_investment",
                    models.BigIntegerField(blank=True, null=True),
                ),
                ("gain_loss_other", models.BigIntegerField(blank=True, null=True)),
                ("reserves", models.BigIntegerField(blank=True, null=True)),
                ("assets_total_fixed", models.BigIntegerField(blank=True, null=True)),
                ("assets_own_use", models.BigIntegerField(blank=True, null=True)),
                (
                    "assets_long_term_investment",
                    models.BigIntegerField(blank=True, null=True),
                ),
                (
                    "defined_benefit_pension_scheme",
                    models.BigIntegerField(blank=True, null=True),
                ),
                ("assets_other_assets", models.BigIntegerField(blank=True, null=True)),
                (
                    "assets_total_liabilities",
                    models.BigIntegerField(blank=True, null=True),
                ),
                (
                    "assets_current_investment",
                    models.BigIntegerField(blank=True, null=True),
                ),
                (
                    "assets_total_assets_and_liabilities",
                    models.BigIntegerField(blank=True, null=True),
                ),
                (
                    "creditors_one_year_total_current",
                    models.BigIntegerField(blank=True, null=True),
                ),
                (
                    "creditors_falling_due_after_one_year",
                    models.BigIntegerField(blank=True, null=True),
                ),
                ("assets_cash", models.BigIntegerField(blank=True, null=True)),
                ("funds_endowment", models.BigIntegerField(blank=True, null=True)),
                ("funds_unrestricted", models.BigIntegerField(blank=True, null=True)),
                ("funds_restricted", models.BigIntegerField(blank=True, null=True)),
                ("funds_total", models.BigIntegerField(blank=True, null=True)),
                ("count_employees", models.IntegerField(blank=True, null=True)),
                ("charity_only_accounts", models.BooleanField(blank=True, null=True)),
                ("consolidated_accounts", models.BooleanField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="CCEWCharityClassification",
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
                ("date_of_extract", models.DateField(blank=True, null=True)),
                ("organisation_number", models.IntegerField()),
                ("registered_charity_number", models.IntegerField(db_index=True)),
                ("linked_charity_number", models.IntegerField(blank=True, null=True)),
                ("classification_code", models.IntegerField(blank=True, null=True)),
                (
                    "classification_type",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "classification_description",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CCEWCharityEventHistory",
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
                ("date_of_extract", models.DateField(blank=True, null=True)),
                ("organisation_number", models.IntegerField()),
                ("registered_charity_number", models.IntegerField(db_index=True)),
                ("linked_charity_number", models.IntegerField(blank=True, null=True)),
                ("charity_name", models.CharField(max_length=255)),
                ("charity_event_order", models.IntegerField(blank=True, null=True)),
                ("event_type", models.CharField(blank=True, max_length=255, null=True)),
                ("date_of_event", models.DateField(blank=True, null=True)),
                ("reason", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "assoc_organisation_number",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "assoc_registered_charity_number",
                    models.IntegerField(blank=True, db_index=True, null=True),
                ),
                (
                    "assoc_charity_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CCEWCharityGoverningDocument",
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
                ("date_of_extract", models.DateField(blank=True, null=True)),
                ("organisation_number", models.IntegerField()),
                ("registered_charity_number", models.IntegerField(db_index=True)),
                ("linked_charity_number", models.IntegerField(blank=True, null=True)),
                (
                    "governing_document_description",
                    models.TextField(blank=True, null=True),
                ),
                ("charitable_objects", models.TextField(blank=True, null=True)),
                ("area_of_benefit", models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="CCEWCharityOtherNames",
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
                ("date_of_extract", models.DateField(blank=True, null=True)),
                ("organisation_number", models.IntegerField()),
                ("registered_charity_number", models.IntegerField(db_index=True)),
                ("linked_charity_number", models.IntegerField(blank=True, null=True)),
                ("charity_name_id", models.IntegerField(blank=True, null=True)),
                (
                    "charity_name_type",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "charity_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CCEWCharityOtherRegulators",
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
                ("date_of_extract", models.DateField(blank=True, null=True)),
                ("organisation_number", models.IntegerField()),
                ("registered_charity_number", models.IntegerField(db_index=True)),
                ("regulator_order", models.IntegerField(blank=True, null=True)),
                (
                    "regulator_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "regulator_web_url",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CCEWCharityPolicy",
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
                ("date_of_extract", models.DateField(blank=True, null=True)),
                ("organisation_number", models.IntegerField()),
                ("registered_charity_number", models.IntegerField(db_index=True)),
                ("linked_charity_number", models.IntegerField()),
                (
                    "policy_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CCEWCharityPublishedReport",
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
                ("date_of_extract", models.DateField(blank=True, null=True)),
                ("charity_id", models.IntegerField()),
                ("registered_charity_number", models.IntegerField(db_index=True)),
                ("linked_charity_number", models.IntegerField(blank=True, null=True)),
                (
                    "report_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "report_location",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("date_published", models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="CCEWCharityTrustee",
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
                ("date_of_extract", models.DateField(blank=True, null=True)),
                ("organisation_number", models.IntegerField()),
                ("registered_charity_number", models.IntegerField(db_index=True)),
                ("linked_charity_number", models.IntegerField()),
                ("trustee_id", models.IntegerField(blank=True, null=True)),
                (
                    "trustee_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("trustee_is_chair", models.BooleanField(blank=True, null=True)),
                (
                    "individual_or_organisation",
                    models.CharField(
                        blank=True,
                        choices=[("P", "Individual"), ("O", "Organisation")],
                        max_length=1,
                        null=True,
                    ),
                ),
                (
                    "trustee_date_of_appointment",
                    models.DateField(blank=True, null=True),
                ),
            ],
        ),
    ]
