import graphene


class AggregationBucket(graphene.ObjectType):
    # Unique across a given aggregation's buckets
    key = graphene.String()

    # Aggregation bucket description
    name = graphene.String()

    # Number of charities in the aggregation bucket
    count = graphene.Int()

    # If the aggregation is on a numerical field e.g. income, the `sum` gives the bucket's cumulative total of that field.
    sum = graphene.Float()


class Aggregation(graphene.ObjectType):
    buckets = graphene.List(AggregationBucket)


class GeoAggregation(graphene.ObjectType):
    geohash = graphene.Field(Aggregation)
    region = graphene.Field(Aggregation)
    country = graphene.Field(Aggregation)


class FinancesAggregation(graphene.ObjectType):
    latestIncome = graphene.Field(Aggregation)
    latestSpending = graphene.Field(Aggregation)


class AggregationTypesCHC(graphene.ObjectType):
    finances = graphene.Field(FinancesAggregation)
    causes = graphene.Field(Aggregation)
    beneficiaries = graphene.Field(Aggregation)
    operations = graphene.Field(Aggregation)
    areas = graphene.Field(Aggregation)

    # Aggregate charities by the geolocation of their registered office.
    # Specify `top`, `bottom`, `left` & `right` arguments to further restrict the search range without affecting the other `getCharities` results.
    # This is useful if you're presenting geo aggregations in a map view.
    geo = graphene.Field(
        GeoAggregation,
        # Latitude defining the portal's top boundary. Default: `90`.
        top=graphene.Float(default_value=90),
        # Longitude defining the portal's left boundary. Default: `-180`.
        left=graphene.Float(default_value=-180),
        # Latitude defining the portal's bottom boundary. Default: `-90`.
        bottom=graphene.Float(default_value=-90),
        # Longitude defining the portal's right boundary. Default: `180`.
        right=graphene.Float(default_value=180),
    )
