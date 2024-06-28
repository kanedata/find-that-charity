import graphene

from findthatcharity.api.graphql.schema.query import QueryCHC


class Query(graphene.ObjectType):
    # Charity Commission of England & Wales
    CHC = graphene.Field(QueryCHC)

    def resolve_CHC(self, info):
        return QueryCHC()


schema = graphene.Schema(query=Query)
