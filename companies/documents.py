from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch.helpers import bulk

from .models import Company


@registry.register_document
class CompanyDocument(Document):

    CompanyNumber = fields.KeywordField(attr="CompanyNumber")
    CompanyStatus = fields.KeywordField(attr="CompanyStatus")
    RegAddress_PostCode = fields.KeywordField(attr="RegAddress_PostCode")
    CompanyCategory = fields.KeywordField(attr="CompanyCategory")
    PreviousNames = fields.TextField()

    def bulk(self, actions, **kwargs):
        if self.django.queryset_pagination and "chunk_size" not in kwargs:
            kwargs["chunk_size"] = self.django.queryset_pagination
        return bulk(client=self._get_connection(), actions=actions, **kwargs)

    def get_queryset(self):
        """
        Return the queryset that should be indexed by this doc type.
        """
        return self.django.model.objects.raw(
            """
            with names as (
                select "org_id",
                    json_agg("CompanyName") as "names"
                from "companies_previousname"
                group by "org_id"
            )
            SELECT c."id",
                c."CompanyNumber",
                c."CompanyName",
                c."CompanyStatus",
                c."RegAddress_PostCode",
                c."CompanyCategory",
                names.names as "PreviousNames"
            FROM "companies_company" c
                left outer join names
                    on c.org_id = names.org_id
        """
        )

    def get_indexing_queryset(self):
        return self.get_queryset()

    class Index:
        # Name of the Elasticsearch index
        name = "companies"
        # See Elasticsearch Indices API reference for available settings
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Company  # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            "CompanyName",
        ]

        # Ignore auto updating of Elasticsearch when a model is saved
        # or deleted:
        ignore_signals = True

        # Don't perform an index refresh after every update (overrides global setting):
        # auto_refresh = False

        # Paginate the django queryset used to populate the index with the specified size
        # (by default it uses the database driver's default setting)
        queryset_pagination = 20000
