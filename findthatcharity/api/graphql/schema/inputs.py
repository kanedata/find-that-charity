import graphene

from .enums import DistanceUnit, GeoCountry, GeoRegion


class NumericRangeInput(graphene.InputObjectType):
    # Greater than or equal to.
    gte = graphene.Float()

    # Greater than.
    gt = graphene.Float()

    # Less than or equal to.
    lte = graphene.Float()

    # Less than.
    lt = graphene.Float()


class DateRangeInput(graphene.InputObjectType):
    # Greater than or equal to. `yyyy-MM-dd`.
    gte = graphene.String()

    # Greater than. `yyyy-MM-dd`.
    gt = graphene.String()

    # Less than or equal to. `yyyy-MM-dd`.
    lte = graphene.String()

    # Less than. `yyyy-MM-dd`.
    lt = graphene.String()


# This input type allows filtering on a field which itself contains a list of values.
class ListFilterInput(graphene.InputObjectType):
    # Require that the field contains all of the provided values (logical AND).
    every = graphene.List(graphene.String)

    # Require that the field contains one or more of the provided values (logical OR).
    some = graphene.List(graphene.String)

    # Require that the field contains none of the provided values (logical AND NOT).
    notSome = graphene.List(graphene.String)

    # Apply conditions to the length of the array field.
    length = graphene.Field(NumericRangeInput)


class GrantsFilterInput(graphene.InputObjectType):
    funders = graphene.Field(ListFilterInput)


class GeoBoundingBoxInput(graphene.InputObjectType):
    # Latitude defining the box's top boundary.
    top = graphene.Float(required=True)

    # Longitude defining the box's left boundary.
    left = graphene.Float(required=True)

    # Latitude defining the box's bottom boundary.
    bottom = graphene.Float(required=True)

    # Longitude defining the box's right boundary.
    right = graphene.Float(required=True)


class GeoBoundingCircleInput(graphene.InputObjectType):
    # Radius of circle.
    radius = graphene.Int(required=True)

    # Unit of circle radius.
    unit = graphene.Field(DistanceUnit, default_value=DistanceUnit.mi)

    # Latitude of circle centre.
    latitude = graphene.Float(required=True)

    # Longitude of circle centre.
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
