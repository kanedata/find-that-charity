import graphene
from django.db.models import Count

from findthatcharity.api.graphql.enums import PageLimit, SocialPlatform, SortCHC
from findthatcharity.apps.charity.models import (
    CCEWCharity,
    CCEWCharityAnnualReturnHistory,
    CCEWCharityAreaOfOperation,
    CCEWCharityClassification,
    CCEWCharityEventHistory,
    CCEWCharityGoverningDocument,
    CCEWCharityOtherNames,
    CCEWCharityTrustee,
)
from findthatcharity.apps.ftc.models import OrganisationLocation
from findthatcharity.apps.ftcprofile.admin import get_connection
from findthatcharity.apps.geo.models import GeoLookup
from findthatcharity.apps.other_data.models import Grant as GrantModel


class FinancialYear(graphene.ObjectType):
    begin = graphene.Date()
    end = graphene.Date()


class FinancialCHC(graphene.ObjectType):
    income = graphene.Float()
    spending = graphene.Float()
    financial_year = graphene.Field(FinancialYear)

    def resolve_income(root, info):
        return root.total_gross_income

    def resolve_spending(root, info):
        return root.total_gross_expenditure

    def resolve_financial_year(root, info):
        return {
            "begin": root.fin_period_start_date,
            "end": root.fin_period_end_date,
        }


class IdName(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()


class Grant(graphene.ObjectType):
    id = graphene.ID()
    title = graphene.String()
    description = graphene.String()
    funder = graphene.Field(IdName)
    funding_organization = graphene.List(
        IdName, deprecation_reason="Use `funder` instead."
    )
    amount_awarded = graphene.Float()
    currency = graphene.String()
    award_date = graphene.Date()

    def resolve_id(root, info):
        return root.grant_id

    def resolve_funder(root, info):
        return {
            "id": root.fundingOrganization_id,
            "name": root.fundingOrganization_name,
        }

    def resolve_funding_organization(root, info):
        return [
            {
                "id": root.fundingOrganization_id,
                "name": root.fundingOrganization_name,
            }
        ]

    def resolve_amount_awarded(root, info):
        return root.amountAwarded

    def resolve_award_date(root, info):
        return root.awardDate


class Funding(graphene.ObjectType):
    funders = graphene.List(IdName)
    grants = graphene.List(Grant)

    def resolve_grants(root, info):
        org_ids = ["GB-CHC-{}".format(root.organisation_number)]
        if root.charity_company_registration_number:
            org_ids.append("GB-COH-{}".format(root.charity_company_registration_number))
        return GrantModel.objects.filter(recipientOrganization_id__in=org_ids)

    def resolve_funders(root, info):
        org_ids = ["GB-CHC-{}".format(root.organisation_number)]
        if root.charity_company_registration_number:
            org_ids.append("GB-COH-{}".format(root.charity_company_registration_number))
        return [
            {
                "id": grant.fundingOrganization_id,
                "name": grant.fundingOrganization_name,
            }
            for grant in GrantModel.objects.filter(recipientOrganization_id__in=org_ids)
            .order_by("fundingOrganization_id")
            .distinct("fundingOrganization_id")
        ]


class GeoCodes(graphene.ObjectType):
    admin_district = graphene.String()
    admin_county = graphene.String()
    admin_ward = graphene.String()
    parish = graphene.String(deprecation_reason="No longer collected")
    parliamentary_constituency = graphene.String()
    ccg = graphene.String(deprecation_reason="No longer collected")
    ced = graphene.String(deprecation_reason="No longer collected")
    nuts = graphene.String(deprecation_reason="No longer collected")

    def resolve_admin_district(root, info):
        return root.geo_laua

    def resolve_admin_county(root, info):
        return root.geo_cty

    def resolve_admin_ward(root, info):
        return root.geo_ward

    def resolve_parliamentary_constituency(root, info):
        return root.geo_pcon


class Geo(graphene.ObjectType):
    postcode = graphene.String()
    quality = graphene.String(deprecation_reason="No longer collected")
    eastings = graphene.Int(deprecation_reason="No longer collected")
    northings = graphene.Int(deprecation_reason="No longer collected")
    country = graphene.String()
    nhs_ha = graphene.String(deprecation_reason="No longer collected")
    longitude = graphene.Float()
    latitude = graphene.Float()
    european_electoral_region = graphene.String(
        deprecation_reason="No longer collected"
    )
    primary_care_trust = graphene.String(deprecation_reason="No longer collected")
    region = graphene.String()
    lsoa = graphene.String()
    msoa = graphene.String()
    incode = graphene.String()
    outcode = graphene.String()
    parliamentary_constituency = graphene.String()
    admin_district = graphene.String()
    parish = graphene.String(deprecation_reason="No longer collected")
    admin_county = graphene.String()
    admin_ward = graphene.String()
    ced = graphene.String(deprecation_reason="No longer collected")
    ccg = graphene.String(deprecation_reason="No longer collected")
    nuts = graphene.String(deprecation_reason="No longer collected")
    codes = graphene.Field(GeoCodes)

    def resolve_postcode(root, info):
        if root.geoCodeType == OrganisationLocation.GeoCodeTypes.POSTCODE:
            return root.geoCode

    def resolve_longitude(root, info):
        return root.geo_long

    def resolve_latitude(root, info):
        return root.geo_lat

    def resolve_codes(root, info):
        return root

    def resolve_country(root, info):
        if root.geo_ctry:
            if root.geo_ctry.startswith("E"):
                return "England"
            if root.geo_ctry.startswith("W"):
                return "Wales"
            if root.geo_ctry.startswith("S"):
                return "Scotland"
            if root.geo_ctry.startswith("N"):
                return "Northern Ireland"

    def resolve_region(root, info):
        geo = GeoLookup.objects.filter(geoCode=root.geo_rgn).first()
        if geo:
            return geo.name

    def resolve_lsoa(root, info):
        return root.geo_lsoa21 or root.geo_lsoa11

    def resolve_msoa(root, info):
        return root.geo_msoa21 or root.geo_msoa11

    def resolve_outcode(root, info):
        if root.geoCodeType == OrganisationLocation.GeoCodeTypes.POSTCODE:
            return root.geoCode[:-3].strip()

    def resolve_incode(root, info):
        if root.geoCodeType == OrganisationLocation.GeoCodeTypes.POSTCODE:
            return root.geoCode[-3:].strip()

    def resolve_parliamentary_constituency(root, info):
        geo = GeoLookup.objects.filter(geoCode=root.geo_pcon).first()
        if geo:
            return geo.name

    def resolve_admin_district(root, info):
        geo = GeoLookup.objects.filter(geoCode=root.geo_laua).first()
        if geo:
            return geo.name

    def resolve_admin_county(root, info):
        geo = GeoLookup.objects.filter(geoCode=root.geo_cty).first()
        if geo:
            return geo.name

    def resolve_admin_ward(root, info):
        geo = GeoLookup.objects.filter(geoCode=root.geo_ward).first()
        if geo:
            return geo.name


class SocialMediaHandle(graphene.ObjectType):
    platform = graphene.Field(SocialPlatform)
    handle = graphene.String()


class ContactCHC(graphene.ObjectType):
    address = graphene.List(graphene.String)
    email = graphene.String()
    person = graphene.String(
        deprecation_reason="The Charity Commission stopped sharing this information."
    )
    phone = graphene.String()
    postcode = graphene.String()
    social = graphene.List(SocialMediaHandle)

    def resolve_address(root, info):
        fields = [
            "charity_contact_address1",
            "charity_contact_address2",
            "charity_contact_address3",
            "charity_contact_address4",
            "charity_contact_address5",
            # "charity_contact_postcode",
        ]
        return [
            getattr(root, field) for field in fields if getattr(root, field) is not None
        ]

    def resolve_postcode(root, info):
        return root.charity_contact_postcode

    def resolve_email(root, info):
        return root.charity_contact_email

    def resolve_phone(root, info):
        return root.charity_contact_phone


class PeopleCHC(graphene.ObjectType):
    employees = graphene.Int()
    trustees = graphene.Int()
    volunteers = graphene.Int()

    def resolve_volunteers(root, info):
        cy = root.current_year()
        if cy:
            return cy.count_volunteers

    def resolve_employees(root, info):
        cy = root.current_year()
        if cy is None:
            return None
        partb = root.current_year().partb()
        if partb is None:
            return None
        return partb.count_employees

    def resolve_trustees(root, info):
        return CCEWCharityTrustee.objects.filter(
            organisation_number=root.organisation_number
        ).count()


class OrgId(graphene.ObjectType):
    id = graphene.ID()
    scheme = graphene.String()
    raw_id = graphene.String()


class Name(graphene.ObjectType):
    value = graphene.String()
    primary = graphene.Boolean()


class RegistrationCHC(graphene.ObjectType):
    registration_date = graphene.Date()
    removal_date = graphene.Date()
    removal_code = graphene.String()
    removal_reason = graphene.String()


class TrusteeCharityCHC(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()

    def resolve_id(root, info):
        return root[0]

    def resolve_name(root, info):
        return root[1]


class TrusteeCHC(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    trusteeships = graphene.Int()
    other_charities = graphene.List(TrusteeCharityCHC)

    def resolve_id(root, info):
        return root.trustee_id

    def resolve_name(root, info):
        return root.trustee_name

    def resolve_trusteeships(root, info):
        return CCEWCharityTrustee.objects.filter(trustee_id=root.trustee_id).count()

    def resolve_other_charities(root, info):
        other_charities = (
            CCEWCharityTrustee.objects.filter(trustee_id=root.trustee_id)
            .exclude(organisation_number=root.organisation_number)
            .values_list("organisation_number", flat=True)
        )
        return CCEWCharity.objects.filter(
            organisation_number__in=other_charities
        ).values_list("registered_charity_number", "charity_name")


class LogoImage(graphene.ObjectType):
    small = graphene.String()
    medium = graphene.String()


class Image(graphene.ObjectType):
    logo = graphene.Field(LogoImage)


class Topic(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    score = graphene.Float()


class CharityCHC(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String(deprecation_reason="Use `names` instead.")
    names = graphene.List(Name, all=graphene.Boolean(default_value=False))
    activities = graphene.String()
    finances = graphene.List(FinancialCHC, all=graphene.Boolean(default_value=False))
    areas = graphene.List(IdName)
    area_of_benefit = graphene.String()
    causes = graphene.List(IdName)
    beneficiaries = graphene.List(IdName)
    operations = graphene.List(IdName)
    funding = graphene.Field(Funding)
    grants = graphene.List(Grant, deprecation_reason="Use `funding.grants` instead.")
    geo = graphene.Field(Geo)
    contact = graphene.Field(ContactCHC)
    website = graphene.String()
    trustees = graphene.List(TrusteeCHC)
    governing_doc = graphene.String()
    objectives = graphene.String()
    num_people = graphene.Field(PeopleCHC)
    org_ids = graphene.List(OrgId)
    financial_year_end = graphene.Date()
    registrations = graphene.List(
        RegistrationCHC, all=graphene.Boolean(default_value=False)
    )
    image = graphene.Field(Image)  # @todo
    topics = graphene.List(Topic)  # @todo

    def resolve_id(root, info):
        return root.registered_charity_number

    def resolve_name(root, info):
        return root.charity_name

    def resolve_names(root, info, all=False):
        default_name = [{"value": root.charity_name, "primary": True}]
        if all:
            return default_name + [
                {"value": name, "primary": False}
                for name in CCEWCharityOtherNames.objects.filter(
                    organisation_number=root.organisation_number
                ).values_list("charity_name", flat=True)
                if name != root.charity_name
            ]
        return default_name

    def resolve_activities(root, info):
        return root.charity_activities

    def resolve_website(root, info):
        return root.charity_contact_web

    def resolve_area_of_benefit(root, info):
        gd = CCEWCharityGoverningDocument.objects.get(
            organisation_number=root.organisation_number
        )
        return gd.area_of_benefit

    def resolve_governing_doc(root, info):
        gd = CCEWCharityGoverningDocument.objects.get(
            organisation_number=root.organisation_number
        )
        return gd.governing_document_description

    def resolve_objectives(root, info):
        gd = CCEWCharityGoverningDocument.objects.get(
            organisation_number=root.organisation_number
        )
        return gd.charitable_objects

    def resolve_causes(root, info):
        categories = CCEWCharityClassification.objects.filter(
            organisation_number=root.organisation_number,
            classification_type="What",
        )
        return [
            {
                "id": category.classification_code,
                "name": category.classification_description,
            }
            for category in categories
        ]

    def resolve_beneficiaries(root, info):
        categories = CCEWCharityClassification.objects.filter(
            organisation_number=root.organisation_number,
            classification_type="Who",
        )
        return [
            {
                "id": category.classification_code,
                "name": category.classification_description,
            }
            for category in categories
        ]

    def resolve_operations(root, info):
        categories = CCEWCharityClassification.objects.filter(
            organisation_number=root.organisation_number,
            classification_type="How",
        )
        return [
            {
                "id": category.classification_code,
                "name": category.classification_description,
            }
            for category in categories
        ]

    def resolve_contact(root, info):
        return root

    def resolve_geo(root, info):
        return OrganisationLocation.objects.filter(
            org_id="GB-CHC-{}".format(root.registered_charity_number),
            locationType=OrganisationLocation.LocationTypes.REGISTERED_OFFICE,
        ).first()

    def resolve_financial_year_end(root, info):
        return root.latest_acc_fin_period_end_date

    def resolve_trustees(root, info):
        return CCEWCharityTrustee.objects.filter(
            organisation_number=root.organisation_number
        ).all()

    def resolve_num_people(root, info):
        return root

    def resolve_org_ids(root, info):
        org_ids = [
            {
                "id": "GB-CHC-{}".format(root.organisation_number),
                "scheme": "GB-CHC",
                "raw_id": root.organisation_number,
            }
        ]
        if root.charity_company_registration_number:
            org_ids.append(
                {
                    "id": "GB-COH-{}".format(root.charity_company_registration_number),
                    "scheme": "GB-COH",
                    "raw_id": root.charity_company_registration_number,
                }
            )
        return org_ids

    def resolve_areas(root, info):
        return [
            {
                "id": area.geographic_area_description,
                "name": area.geographic_area_description,
            }
            for area in CCEWCharityAreaOfOperation.objects.filter(
                organisation_number=root.organisation_number
            )
        ]

    def resolve_finances(root, info, all):
        if all:
            return CCEWCharityAnnualReturnHistory.objects.filter(
                organisation_number=root.organisation_number
            ).order_by("-fin_period_end_date")
        return [
            CCEWCharityAnnualReturnHistory(
                **{
                    "fin_period_start_date": root.latest_acc_fin_period_start_date,
                    "fin_period_end_date": root.latest_acc_fin_period_end_date,
                    "total_gross_income": root.latest_income,
                    "total_gross_expenditure": root.latest_expenditure,
                }
            )
        ]

    def resolve_registrations(root, info, all):
        removal_reason = None
        if root.date_of_removal:
            removal_event = CCEWCharityEventHistory.objects.filter(
                organisation_number=root.organisation_number,
                date_of_event=root.date_of_removal,
                reason__isnull=False,
            ).first()
            if removal_event:
                removal_reason = removal_event.reason
        return [
            {
                "registration_date": root.date_of_registration,
                "removal_date": root.date_of_removal,
                "removal_reason": removal_reason,
                "removal_code": removal_reason,
            }
        ]

    def resolve_grants(root, info):
        org_ids = ["GB-CHC-{}".format(root.organisation_number)]
        if root.charity_company_registration_number:
            org_ids.append("GB-COH-{}".format(root.charity_company_registration_number))
        return GrantModel.objects.filter(recipientOrganization_id__in=org_ids)

    def resolve_funding(root, info):
        return root


class AggregationBucket(graphene.ObjectType):
    key = graphene.String()
    name = graphene.String()
    count = graphene.Int()
    sum = graphene.Float()


class Aggregation(graphene.ObjectType):
    buckets = graphene.List(AggregationBucket)


class GeoAggregation(graphene.ObjectType):
    geohash = graphene.Field(Aggregation)
    region = graphene.Field(Aggregation)
    country = graphene.Field(Aggregation)

    query = """
        with hq as (
            select l.org_id, g."{area_field}" as area_code, g.name as area_name
            from "{location_table}" l 
                inner join "{geolookup_table}" g 
                    on l."{area_field}" = g."geoCode" 
            where l."locationType" = %(location_type)s
                and l.geo_lat <= %(top)s
                and l.geo_lat >= %(bottom)s
                and l.geo_long <= %(right)s
                and l.geo_long >= %(left)s
        )
        select hq.area_code, hq.area_name, count(*), sum(latest_income)
        from "{charity_table}" c
            inner join hq
                on ('GB-CHC-' || c.registered_charity_number) = hq.org_id
        where c.organisation_number in %(organisation_numbers)s
        group by 1, 2
        """

    def resolve_region(root, info):
        connection = get_connection(CCEWCharity)
        organisation_numbers = tuple(
            root["query"].values_list("organisation_number", flat=True)
        )
        with connection.cursor() as cursor:
            cursor.execute(
                GeoAggregation.query.format(
                    charity_table=CCEWCharity._meta.db_table,
                    area_field="geo_rgn",
                    location_table=OrganisationLocation._meta.db_table,
                    geolookup_table=GeoLookup._meta.db_table,
                ),
                params={
                    "location_type": OrganisationLocation.LocationTypes.REGISTERED_OFFICE,
                    "organisation_numbers": organisation_numbers,
                    "top": root["top"],
                    "bottom": root["bottom"],
                    "left": root["left"],
                    "right": root["right"],
                },
            )
            return {
                "buckets": [
                    {
                        "key": cause[0],
                        "name": cause[1],
                        "count": cause[2],
                        "sum": cause[3],
                    }
                    for cause in cursor.fetchall()
                ]
            }

    def resolve_country(root, info):
        connection = get_connection(CCEWCharity)
        organisation_numbers = tuple(
            root["query"].values_list("organisation_number", flat=True)
        )
        with connection.cursor() as cursor:
            cursor.execute(
                GeoAggregation.query.format(
                    charity_table=CCEWCharity._meta.db_table,
                    area_field="geo_ctry",
                    location_table=OrganisationLocation._meta.db_table,
                    geolookup_table=GeoLookup._meta.db_table,
                ),
                params={
                    "location_type": OrganisationLocation.LocationTypes.REGISTERED_OFFICE,
                    "organisation_numbers": organisation_numbers,
                    "top": root["top"],
                    "bottom": root["bottom"],
                    "left": root["left"],
                    "right": root["right"],
                },
            )
            return {
                "buckets": [
                    {
                        "key": cause[0],
                        "name": cause[1],
                        "count": cause[2],
                        "sum": cause[3],
                    }
                    for cause in cursor.fetchall()
                ]
            }


class FinancesAggregation(graphene.ObjectType):
    latest_income = graphene.Field(Aggregation)
    latest_spending = graphene.Field(Aggregation)

    query = """
        WITH a AS (
            SELECT organisation_number,
                "{field_name}" as value
            FROM "{table_name}"
            WHERE organisation_number in %s
        ),
        b AS (
            SELECT CASE 
                WHEN value >= 1000000000 THEN '[9, "Min. £1000000000"]'::JSONB
                WHEN value >= 316227766 THEN '[8.5, "Min. £316227766"]'::JSONB
                WHEN value >= 100000000 THEN '[8, "Min. £100000000"]'::JSONB
                WHEN value >= 31622777 THEN '[7.5, "Min. £31622777"]'::JSONB
                WHEN value >= 10000000 THEN '[7, "Min. £10000000"]'::JSONB
                WHEN value >= 3162278 THEN '[6.5, "Min. £3162278"]'::JSONB
                WHEN value >= 1000000 THEN '[6, "Min. £1000000"]'::JSONB
                WHEN value >= 316228 THEN '[5.5, "Min. £316228"]'::JSONB
                WHEN value >= 100000 THEN '[5, "Min. £100000"]'::JSONB
                WHEN value >= 31623 THEN '[4.5, "Min. £31623"]'::JSONB
                WHEN value >= 10000 THEN '[4, "Min. £10000"]'::JSONB
                WHEN value >= 3162 THEN '[3.5, "Min. £3162"]'::JSONB
                WHEN value >= 1000 THEN '[3, "Min. £1000"]'::JSONB
                WHEN value >= 316 THEN '[2.5, "Min. £316"]'::JSONB
                WHEN value >= 100 THEN '[2, "Min. £100"]'::JSONB
                WHEN value >= 32 THEN '[1.5, "Min. £32"]'::JSONB
                WHEN value >= 10 THEN '[1, "Min. 10"]'::JSONB
                WHEN value >= 3 THEN '[0.5, "Min. £3"]'::JSONB
                WHEN value >= 1 THEN '[0, "Min. £1"]'::JSONB
                ELSE '[-99, "Unknown"]'::JSONB END as banded,
                COUNT(*) AS count,
                SUM(value) AS sum
            FROM a
            GROUP BY 1
        )
        SELECT banded->>0 as key, banded->>1 as name, count, sum
        FROM b
        """

    def resolve_latest_income(root, info):
        connection = get_connection(CCEWCharity)
        organisation_numbers = tuple(root.values_list("organisation_number", flat=True))
        with connection.cursor() as cursor:
            cursor.execute(
                FinancesAggregation.query.format(
                    table_name=CCEWCharity._meta.db_table, field_name="latest_income"
                ),
                params=(organisation_numbers,),
            )
            return {
                "buckets": [
                    {
                        "key": cause[0],
                        "name": cause[1],
                        "count": cause[2],
                        "sum": cause[3],
                    }
                    for cause in cursor.fetchall()
                ]
            }

    def resolve_latest_spending(root, info):
        connection = get_connection(CCEWCharity)
        organisation_numbers = tuple(root.values_list("organisation_number", flat=True))
        with connection.cursor() as cursor:
            cursor.execute(
                FinancesAggregation.query.format(
                    table_name=CCEWCharity._meta.db_table,
                    field_name="latest_expenditure",
                ),
                params=(organisation_numbers,),
            )
            return {
                "buckets": [
                    {
                        "key": cause[0],
                        "name": cause[1],
                        "count": cause[2],
                        "sum": cause[3],
                    }
                    for cause in cursor.fetchall()
                ]
            }


class AggregationTypesCHC(graphene.ObjectType):
    finances = graphene.Field(FinancesAggregation)
    causes = graphene.Field(Aggregation)
    beneficiaries = graphene.Field(Aggregation)
    operations = graphene.Field(Aggregation)
    areas = graphene.Field(Aggregation)
    geo = graphene.Field(
        GeoAggregation,
        top=graphene.Float(default_value=90),
        left=graphene.Float(default_value=-180),
        bottom=graphene.Float(default_value=-90),
        right=graphene.Float(default_value=180),
    )

    def resolve_finances(root, info):
        return root

    def resolve_geo(root, info, top, left, bottom, right):
        return {
            "query": root,
            "top": top,
            "left": left,
            "bottom": bottom,
            "right": right,
        }

    def resolve_causes(root, info):
        return {
            "buckets": [
                {
                    "key": cause["classification_code"],
                    "name": cause["classification_description"],
                    "count": cause["count"],
                    "sum": None,
                }
                for cause in CCEWCharityClassification.objects.filter(
                    classification_type="What",
                    organisation_number__in=root.values_list(
                        "organisation_number", flat=True
                    ),
                )
                .values("classification_code", "classification_description")
                .annotate(count=Count("classification_code"))
            ]
        }

    def resolve_beneficiaries(root, info):
        return {
            "buckets": [
                {
                    "key": cause["classification_code"],
                    "name": cause["classification_description"],
                    "count": cause["count"],
                    "sum": None,
                }
                for cause in CCEWCharityClassification.objects.filter(
                    classification_type="Who",
                    organisation_number__in=root.values_list(
                        "organisation_number", flat=True
                    ),
                )
                .values("classification_code", "classification_description")
                .annotate(count=Count("classification_code"))
            ]
        }

    def resolve_operations(root, info):
        return {
            "buckets": [
                {
                    "key": cause["classification_code"],
                    "name": cause["classification_description"],
                    "count": cause["count"],
                    "sum": None,
                }
                for cause in CCEWCharityClassification.objects.filter(
                    classification_type="How",
                    organisation_number__in=root.values_list(
                        "organisation_number", flat=True
                    ),
                )
                .values("classification_code", "classification_description")
                .annotate(count=Count("classification_code"))
            ]
        }

    def resolve_areas(root, info):
        return {
            "buckets": [
                {
                    "key": cause["geographic_area_description"],
                    "name": cause["geographic_area_description"],
                    "count": cause["count"],
                    "sum": None,
                }
                for cause in CCEWCharityAreaOfOperation.objects.filter(
                    organisation_number__in=root.values_list(
                        "organisation_number", flat=True
                    ),
                )
                .values("geographic_area_description")
                .annotate(count=Count("geographic_area_description"))
            ]
        }


class DownloadCHC(graphene.ObjectType):
    name = graphene.String()
    size = graphene.Int()
    url = graphene.String()


class FilteredCharitiesCHC(graphene.ObjectType):
    count = graphene.Int()
    list = graphene.List(
        CharityCHC,
        limit=graphene.Argument(PageLimit, default_value=10),
        skip=graphene.Int(default_value=0),
        sort=graphene.Argument(SortCHC, default_value=SortCHC.default),
    )
    aggregate = graphene.Field(AggregationTypesCHC)
    download = graphene.Field(DownloadCHC)

    def resolve_count(root, info):
        return root.count()

    def resolve_list(root, info, limit, skip, sort):
        return root[skip : skip + limit]

    def resolve_aggregate(root, info):
        return root


class FilterCHC(graphene.ObjectType):
    id = graphene.ID()
    value = graphene.String()
    label = graphene.String()
    filter_type = graphene.String()
    score = graphene.Float()


# potentialreplacement SQL query
"""
with names as (
	select organisation_number,
		jsonb_agg(
			jsonb_build_object(
				'value', charity_name, 'primary', false
			)
		) as names
	from charity_ccewcharityothernames
	group by 1
),
finances as (
	select organisation_number,
		jsonb_agg(
			jsonb_build_object(
				'income', total_gross_income , 'spending', total_gross_expenditure, 'financial_year', jsonb_build_object(
					'begin', fin_period_start_date, 'end', fin_period_end_date 
				) 
			)
		) as finances
	from charity_ccewcharityannualreturnhistory
	group by 1
)
select cc.registered_charity_number as id,
	cc.charity_name as name,
	names.names,
	cc.charity_activities as activities,
	finances.finances,
	null as areas,
	gd.area_of_benefit,
	null as causes,
	null as beneficiaries,
	null as operations,
	null as funding,
	null as grants,
	null as geo,
	jsonb_build_object(
		'address',
		jsonb_build_array(
			cc.charity_contact_address1,
			cc.charity_contact_address2,
			cc.charity_contact_address3,
			cc.charity_contact_address4,
			cc.charity_contact_address5 
		),
		'email',
		cc.charity_contact_email,
		'person',
		null,
		'phone',
		cc.charity_contact_phone,
		'postcode',
		cc.charity_contact_postcode,
		'social',
		null
	)  as contact,
	cc.charity_contact_web as website,
	null as trustees,
	gd.governing_document_description as governing_doc,
	gd.charitable_objects as objectives,
	null as num_people,
	null as org_ids,
	cc.latest_acc_fin_period_end_date as financial_year_end,
	null as registrations,
	null as image,
	null as topic
from charity_ccewcharity cc 
	left outer join names
		on cc.organisation_number = names.organisation_number
	left outer join finances
		on cc.organisation_number = finances.organisation_number
	left outer join charity_ccewcharitygoverningdocument gd
		on cc.organisation_number = gd.organisation_number 
where cc.linked_charity_number = 0;
"""
