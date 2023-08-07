import graphene

from findthatcharity.api.graphql.inputs import FilterCHCInput
from findthatcharity.api.graphql.object_types import FilterCHC, FilteredCharitiesCHC
from findthatcharity.apps.charity.models import CCEWCharity


class QueryCHC(graphene.ObjectType):
    get_charities = graphene.Field(
        FilteredCharitiesCHC, filters=graphene.Argument(FilterCHCInput)
    )
    get_filters = graphene.List(
        FilterCHC,
        search=graphene.String(),
        id=graphene.List(graphene.String),
        filter_type=graphene.String(),
    )

    def resolve_get_charities(root, info, filters):
        query = CCEWCharity.objects
        where_clause = ["(linked_charity_number = 0)"]
        joins = []
        if filters.get("id"):
            where_clause.append("(registered_charity_number IN %(id)s)")
        if filters.get("search"):
            where_clause.append("(charity_name ILIKE %(search)s)")

        query = CCEWCharity.objects.raw(
            """
            SELECT *
            FROM charity_ccewcharity
            {joins}
            WHERE {where_clause}""".format(
                where_clause=" AND ".join(where_clause), joins=" ".join(joins)
            ),
            params=filters,
        )

        return query


class Query(graphene.ObjectType):
    CHC = graphene.Field(QueryCHC)

    def resolve_CHC(root, info, **kwargs):
        return QueryCHC()


schema = graphene.Schema(query=Query)
