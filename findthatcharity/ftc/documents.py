from collections import defaultdict

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Organisation


@registry.register_document
class FullOrganisation(Document):

    org_id = fields.KeywordField()
    complete_names = fields.CompletionField()
    orgIDs = fields.KeywordField()
    alternateName = fields.TextField()
    organisationType = fields.KeywordField()
    source = fields.KeywordField()

    class Index:
        # Name of the Elasticsearch index
        name = 'ftc_organisation'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    def prepare_complete_names(self, instance):
        words = set()
        for n in instance.alternateName + [instance.name]:
            if n:
                w = n.split()
                words.update([" ".join(w[r:]) for r in range(len(w))])
        return list(words)

    def _prepare_action(self, object_instance, action):
        result = super(FullOrganisation, self)._prepare_action(object_instance, action)
        result['_id'] = object_instance.org_id
        return result

    def prepare_orgIDs(self, instance):
        return instance.orgIDs

    def prepare_alternateName(self, instance):
        return instance.alternateName

    def prepare_organisationType(self, instance):
        return instance.organisationType

    def prepare_source(self, instance):
        return instance.source_id

    def prepare_org_id(self, instance):
        return str(instance.org_id)

    def get_queryset(self):
        """
        Return the queryset that should be indexed by this doc type.
        """
        sql = """
        select distinct on (o."linked_orgs") o.*
        from (
            select *
            from ftc_organisation 
            order by active desc, "dateRemoved" desc, "dateRegistered" desc
        ) as o
        """

        return self.django.model.objects.raw(sql)

    def get_indexing_queryset(self):
        """
        Build queryset (iterator) for use by indexing.
        """
        qs = self.get_queryset()
        kwargs = {}
        if DJANGO_VERSION >= (2,) and self.django.queryset_pagination:
            kwargs = {'chunk_size': self.django.queryset_pagination}
        return qs.iterator(**kwargs)

    class Django:
        model = Organisation  # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'name',
            'postalCode',
            'dateModified',
            'active',
        ]

        # Ignore auto updating of Elasticsearch when a model is saved
        # or deleted:
        ignore_signals = True

        # Don't perform an index refresh after every update (overrides global setting):
        auto_refresh = False

        # Paginate the django queryset used to populate the index with the specified size
        # (by default it uses the database driver's default setting)
        # queryset_pagination = 5000

    def get_related_orgs(self):
        return Organisation.objects.filter(org_id__in=self.orgIDs)
