import graphene

from findthatcharity.api.graphql.enums import DistanceUnit, GeoCountry, GeoRegion


class NumericRangeInput(graphene.InputObjectType):
    gte = graphene.Float()
    lte = graphene.Float()
    gt = graphene.Float()
    lt = graphene.Float()


class DateRangeInput(graphene.InputObjectType):
    gte = graphene.Date()
    lte = graphene.Date()
    gt = graphene.Date()
    lt = graphene.Date()


class ListFilterInput(graphene.InputObjectType):
    every = graphene.List(graphene.String)
    some = graphene.List(graphene.String)
    not_some = graphene.List(graphene.String)
    length = graphene.Field(NumericRangeInput)


class GrantsFilterInput(graphene.InputObjectType):
    funders = graphene.Field(ListFilterInput)


class GeoBoundingBoxInput(graphene.InputObjectType):
    top = graphene.Float(required=True)
    left = graphene.Float(required=True)
    bottom = graphene.Float(required=True)
    right = graphene.Float(required=True)


class GeoBoundingCircleInput(graphene.InputObjectType):
    radius = graphene.Int(required=True)
    unit = graphene.Field(DistanceUnit, default_value=DistanceUnit.mi)
    latitude = graphene.Float(required=True)
    longitude = graphene.Float(required=True)


class GeoFilterInput(graphene.InputObjectType):
    bounding_box = graphene.Field(GeoBoundingBoxInput)
    bounding_circle = graphene.Field(GeoBoundingCircleInput)
    geohashes = graphene.List(graphene.String)
    region = graphene.Field(GeoRegion)
    country = graphene.Field(GeoCountry)
    laua = graphene.String()


class FinancesFilterInput(graphene.InputObjectType):
    latest_income = graphene.Field(NumericRangeInput)
    latest_spending = graphene.Field(NumericRangeInput)


class RegistrationsFilterInput(graphene.InputObjectType):
    latest_registration_date = graphene.Field(DateRangeInput)


class ImageFilterInput(graphene.InputObjectType):
    small_logo_exists = graphene.Boolean()
    medium_logo_exists = graphene.Boolean()


class SocialFilterInput(graphene.InputObjectType):
    twitter_exists = graphene.Boolean()
    facebook_exists = graphene.Boolean()
    instagram_exists = graphene.Boolean()


class FilterCHCInput(graphene.InputObjectType):
    id = graphene.List(graphene.ID)
    search = graphene.String()
    areas = graphene.Field(ListFilterInput)
    causes = graphene.Field(ListFilterInput)
    beneficiaries = graphene.Field(ListFilterInput)
    operations = graphene.Field(ListFilterInput)
    grants = graphene.Field(GrantsFilterInput)
    geo = graphene.Field(GeoFilterInput)
    finances = graphene.Field(FinancesFilterInput)
    registrations = graphene.Field(RegistrationsFilterInput)
    trustees = graphene.Field(ListFilterInput)
    topics = graphene.Field(ListFilterInput)
    image = graphene.Field(ImageFilterInput)
    social = graphene.Field(SocialFilterInput)
