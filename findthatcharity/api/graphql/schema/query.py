from functools import reduce

import graphene
from django.db.models import Q
from pygeohash import decode_exactly

from findthatcharity.api.graphql.schema.aggregation import AggregationTypesCHC
from findthatcharity.api.graphql.schema.chc import CharityCHC
from findthatcharity.api.graphql.schema.enums import (
    PageLimit,
    SortCHC,
)
from findthatcharity.api.graphql.schema.inputs import FilterCHCInput
from ftc.models import CharityData


class DownloadCHC(graphene.ObjectType):
    # Name of output file
    name = graphene.String()

    # Content-Length of output file
    size = graphene.Int()

    # URL of output file
    url = graphene.String()


class FilteredCharitiesCHC(graphene.ObjectType):
    # Various formats to represent filtered charities

    count = graphene.Int()  # Number of charities matching query

    # List of charities matching query
    list = graphene.List(
        CharityCHC,
        limit=graphene.Argument(PageLimit, default_value=10),
        skip=graphene.Int(default_value=0),
        sort=graphene.Argument(SortCHC, default_value=SortCHC.default),
    )

    # Aggregations of charities matching query
    aggregate = graphene.Field(AggregationTypesCHC)

    # Returns a CSV containing all matches.
    download = graphene.Field(DownloadCHC)

    def resolve_count(root, info):
        return root.count()

    def resolve_list(root, info, limit, skip, sort):
        return root[skip : skip + limit]


class FilterCHC(graphene.ObjectType):
    id = graphene.ID()
    value = graphene.String()
    label = graphene.String()
    filterType = graphene.String()
    score = graphene.Float()


class QueryCHC(graphene.ObjectType):
    # Query charities registered in England & Wales
    get_charities = graphene.Field(
        FilteredCharitiesCHC, filters=graphene.Argument(FilterCHCInput, required=True)
    )
    get_filters = graphene.List(
        FilterCHC,
        search=graphene.String(),  # Search term for finding filters.
        id=graphene.List(graphene.ID),  # List of IDs of desired filters.
        filterType=graphene.List(graphene.String),  # List of filter types to return.
    )

    def resolve_get_charities(root, info, filters=None):
        # get annotations
        base_query = CharityData.objects.filter(source="ccew", active=True)

        if filters.get("id"):
            base_query = base_query.filter(Q(id__in=filters.get("id")))

        if filters.get("search"):
            base_query = base_query.filter(
                Q(
                    Q(data__name__icontains=filters.get("search"))
                    | Q(data__activities__icontains=filters.get("search"))
                )
            )

        if filters.get("grants") and filters.get("grants", {}).get("funders"):
            filters["funders"] = filters["grants"]["funders"]

        for field in [
            "areas",
            "causes",
            "beneficiaries",
            "operations",
            "trustees",
            "funders",
        ]:
            if filters.get(field):
                if filters.get(field, {}).get("some"):
                    base_query = base_query.filter(
                        Q(**{f"{field}_list__overlap": filters[field]["some"]})
                    )
                if filters.get(field, {}).get("every"):
                    base_query = base_query.filter(
                        Q(**{f"{field}_list__contains": filters[field]["every"]})
                    )
                if filters.get(field, {}).get("notSome"):
                    base_query = base_query.exclude(
                        Q(**{f"{field}_list__overlap": filters[field]["notSome"]})
                    )
                if filters.get(field, {}).get("length"):
                    for operator in ["gte", "gt", "lte", "le"]:
                        if filters.get(field, {}).get("length", {}).get(operator):
                            db_field = f"{field}_list__len__{operator}"
                            base_query = base_query.filter(
                                Q(**{db_field: filters[field]["length"][operator]})
                            )

        for field in ["latest_income", "latest_spending"]:
            if filters.get("finances") and filters.get("finances", {}).get(field):
                for operator in ["gte", "gt", "lte", "le"]:
                    if filters.get("finances", {}).get(field, {}).get(operator):
                        db_field = f"data__finances__0__{field}__{operator}".replace(
                            "latest_", ""
                        )
                        base_query = base_query.exclude(
                            Q(**{db_field: filters["finances"][field][operator]})
                        )

        if filters.get("registrations") and filters.get("registrations", {}).get(
            "latest_registration_date"
        ):
            reg_date_filter = filters["registrations"]["latest_registration_date"]
            for operator in ["gte", "gt", "lte", "le"]:
                if reg_date_filter.get(operator):
                    db_field = "registration_date__" + operator
                    base_query = base_query.filter(
                        Q(**{db_field: reg_date_filter[operator]})
                    )

        if filters.get("social"):
            if filters.get("social", {}).get("twitter_exists"):
                base_query = base_query.filter(Q(social_twitter=True))
            if filters.get("social", {}).get("facebook_exists"):
                base_query = base_query.filter(Q(social_facebook=True))

        if filters.get("geo"):
            for field in ["region", "country", "laua"]:
                if filters.get("geo", {}).get(field):
                    db_field = f"{field}_code"
                    base_query = base_query.filter(
                        Q(**{db_field: filters["geo"][field]})
                    )
            if filters.get("geo", {}).get("bounding_box"):
                bounding_box = filters["geo"]["bounding_box"]
                base_query = base_query.filter(
                    latitude__gte=bounding_box["top"],
                    latitude__lte=bounding_box["bottom"],
                    longitude__gte=bounding_box["left"],
                    longitude__lte=bounding_box["right"],
                )
            if filters.get("geo", {}).get("geohashes"):
                geo_hash = []
                for gh in filters["geo"]["geohashes"]:
                    lat, lon, lat_err, lon_err = decode_exactly(gh)
                    geo_hash.append(
                        Q(
                            latitude__gte=lat - lat_err,
                            latitude__lte=lat + lat_err,
                            longitude__gte=lon - lon_err,
                            longitude__lte=lon + lon_err,
                        )
                    )
                base_query = base_query.filter(reduce(Q.__or__, geo_hash))

        return base_query.values_list("data", flat=True)

    def resolve_get_filters(root, info, search=None, id=None, filterType=None):
        return [
            {
                "id": "123",
                "value": "value",
                "label": "label",
                "filterType": "filterType",
                "score": 0.5,
            }
        ]
