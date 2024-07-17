import graphene
from django.db.models import F, Q
from django_cte import With

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
        base_query = CharityData.objects.filter(source="ccew", active=True).values(
            "id", "data"
        )
        used_filters = []
        used_exclusions = []

        if filters.get("id"):
            used_filters.append(Q(id__in=filters.get("id")))

        if filters.get("search"):
            used_filters.append(
                Q(
                    Q(data__name__icontains=filters.get("search"))
                    | Q(data__activities__icontains=filters.get("search"))
                )
            )

        for field in ["causes", "beneficiaries", "operations"]:
            if filters.get(field):
                base_query = base_query.annotate(**{field: F(f"data__{field}")})
                if filters.get(field, {}).get("some"):
                    used_filters.append(
                        Q(**{f"{field}__overlap": filters[field]["some"]})
                    )
                if filters.get(field, {}).get("every"):
                    used_filters.append(
                        Q(**{f"{field}__contains": filters[field]["every"]})
                    )
                if filters.get(field, {}).get("notSome"):
                    used_exclusions.append(
                        Q(**{f"{field}__overlap": filters[field]["notSome"]})
                    )
                if filters.get(field, {}).get("length"):
                    for operator in ["gte", "gt", "lte", "le"]:
                        if filters.get(field, {}).get("length", {}).get(operator):
                            db_field = f"{field}__len__{operator}"
                            used_filters.append(
                                Q(**{db_field: filters[field]["length"][operator]})
                            )

        for field in ["latest_income", "latest_spending"]:
            if filters.get("finances") and filters.get("finances", {}).get(field):
                for operator in ["gte", "gt", "lte", "le"]:
                    if filters.get("finances", {}).get(field, {}).get(operator):
                        db_field = f"data__finances__0__{field}__{operator}".replace(
                            "latest_", ""
                        )
                        used_filters.append(
                            Q(**{db_field: filters["finances"][field][operator]})
                        )

        # areas = graphene.Field(ListFilterInput)
        # causes = graphene.Field(ListFilterInput)
        # beneficiaries = graphene.Field(ListFilterInput)
        # operations = graphene.Field(ListFilterInput)
        # grants = graphene.Field(GrantsFilterInput)
        # geo = graphene.Field(GeoFilterInput)
        # finances = graphene.Field(FinancesFilterInput)
        # registrations = graphene.Field(RegistrationsFilterInput)
        # trustees = graphene.Field(ListFilterInput)
        # topics = graphene.Field(ListFilterInput)
        # image = graphene.Field(ImageFilterInput)
        # social = graphene.Field(SocialFilterInput)

        charities_cte = With(base_query)
        charities = (
            charities_cte.queryset()
            .with_cte(charities_cte)
            .filter(*used_filters)
            .exclude(*used_exclusions)
        )

        print(charities.query)

        return charities.values_list("data", flat=True)

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
