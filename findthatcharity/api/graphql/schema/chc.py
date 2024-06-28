from datetime import date

import graphene

from findthatcharity.api.graphql.schema.enums import SocialPlatform


class FinancialYear(graphene.ObjectType):
    begin = graphene.Date()
    end = graphene.Date()

    def resolve_begin(root, info):
        return date.fromisoformat(root["begin"])

    def resolve_end(root, info):
        return date.fromisoformat(root["end"])


class FinancialCHC(graphene.ObjectType):
    income = graphene.Float()
    spending = graphene.Float()
    financial_year = graphene.Field(FinancialYear)


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

    def resolve_award_date(root, info):
        return date.fromisoformat(root["award_date"])

    def resolve_funding_organization(root, info):
        return [root["funder"]]


class Funding(graphene.ObjectType):
    funders = graphene.List(IdName)
    grants = graphene.List(Grant)


class GeoCodes(graphene.ObjectType):
    admin_district = graphene.String()
    admin_county = graphene.String()
    admin_ward = graphene.String()
    parish = graphene.String(deprecation_reason="No longer included")
    parliamentary_constituency = graphene.String()
    ccg = graphene.String(deprecation_reason="No longer included")
    ced = graphene.String(deprecation_reason="No longer included")
    nuts = graphene.String(deprecation_reason="No longer included")


class Geo(graphene.ObjectType):
    postcode = graphene.String()
    quality = graphene.String(deprecation_reason="No longer included")
    eastings = graphene.Int()
    northings = graphene.Int()
    country = graphene.String()
    nhs_ha = graphene.String(name="nhs_ha", deprecation_reason="No longer included")
    longitude = graphene.Float()
    latitude = graphene.Float()
    european_electoral_region = graphene.String(
        name="european_electoral_region", deprecation_reason="No longer included"
    )
    primary_care_trust = graphene.String(
        name="primary_care_trust", deprecation_reason="No longer included"
    )
    region = graphene.String()
    lsoa = graphene.String()
    msoa = graphene.String()
    incode = graphene.String()
    outcode = graphene.String()
    parliamentary_constituency = graphene.String(name="parliamentary_constituency")
    admin_district = graphene.String(name="admin_district")
    parish = graphene.String(deprecation_reason="No longer included")
    admin_county = graphene.String(name="admin_county")
    admin_ward = graphene.String(name="admin_ward")
    ced = graphene.String(deprecation_reason="No longer included")
    ccg = graphene.String(deprecation_reason="No longer included")
    nuts = graphene.String(deprecation_reason="No longer included")
    codes = graphene.Field(GeoCodes)


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


class PeopleCHC(graphene.ObjectType):
    employees = graphene.Int()
    trustees = graphene.Int()
    volunteers = graphene.Int()


class OrgId(graphene.ObjectType):
    id = graphene.ID()
    scheme = graphene.String()
    raw_id = graphene.String()

    def resolve_id(root, info):
        return f"{root['scheme']}-{root['raw_id']}"


class Name(graphene.ObjectType):
    value = graphene.String()
    primary = graphene.Boolean()

    def resolve_value(root, info):
        if "value" in root:
            return root["value"]
        return root["name"]


class RegistrationCHC(graphene.ObjectType):
    registration_date = graphene.Date()
    removal_date = graphene.Date()
    removal_code = graphene.String()
    removal_reason = graphene.String()


class TrusteeCharityCHC(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()


class TrusteeCHC(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    trusteeships = graphene.Int()
    other_charities = graphene.List(TrusteeCharityCHC)


class LogoImage(graphene.ObjectType):
    # URL of a small logo suitable for rendering in a list of charity avatars. The exact dimensions may vary.  URL is valid for 24 hours after the request.
    small = graphene.String()

    # URL of a medium logo suitable for rendering in a charity profile page. The exact dimensions may vary.  URL is valid for 24 hours after the request.
    medium = graphene.String()


class Image(graphene.ObjectType):
    logo = graphene.Field(LogoImage)


# Thematic category auto-generated using topic modelling.
# **Warning:** this feature is experimental and the topics are dynamic.
# Both their names and ids are likely to change each month.
class Topic(graphene.ObjectType):
    # Topic ID.
    # **Warning:** topics are dynamic so a particular ID might not exist in the future.
    # Use `CHC.getFilters` to search currently available topics.
    id = graphene.ID()

    # A space-separated list of words relevant to the topic.
    name = graphene.String()

    # A numerical value between `0` and `1`.
    # A high value corresponds to a high likelihood that the topic is relevant to the Charity.
    score = graphene.Float()


# Charity registered in England & Wales
class CharityCHC(graphene.ObjectType):
    id = graphene.ID()

    # Registered name of the charity
    name = graphene.String(deprecation_reason="Use `names` instead.")
    names = graphene.List(
        Name,
        # If `true` then all working names are returned
        all=graphene.Boolean(default_value=False),
    )

    # Short description of the charity's activities
    activities = graphene.String()
    finances = graphene.List(
        FinancialCHC,
        # If `true` then all annual finances are returned
        all=graphene.Boolean(default_value=False),
    )

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
    financial_year_end = graphene.String()
    registrations = graphene.List(
        RegistrationCHC,
        # If `true` then all previous registrations are returned
        all=graphene.Boolean(default_value=False),
    )
    image = graphene.Field(
        Image, deprecation_reason="Not included in Find that Charity"
    )
    topics = graphene.List(
        Topic, deprecation_reason="Not included in Find that Charity"
    )

    def resolve_grants(root, info):
        return root["funding"].get("grants")

    def resolve_finances(root, info, all=False):
        if len(root["finances"]) > 1:
            if all:
                return root["finances"]
            return [root["finances"][0]]
        return root["finances"]

    def resolve_names(root, info, all=False):
        if all:
            return root["names"]
        primary_names = [name for name in root["names"] if name["primary"]]
        return [primary_names[0]]

    def resolve_causes(root, info):
        return [{"id": value, "name": None} for value in root["causes"]]

    def resolve_beneficiaries(root, info):
        return [{"id": value, "name": None} for value in root["beneficiaries"]]

    def resolve_operations(root, info):
        return [{"id": value, "name": None} for value in root["operations"]]
