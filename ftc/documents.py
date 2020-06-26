from collections import defaultdict

from django.core.paginator import Paginator, Page
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.search import Search
from django_elasticsearch_dsl.registries import registry
from elasticsearch.helpers import bulk
from elasticsearch_dsl.field import Completion
from elasticsearch_dsl.connections import get_connection
import tqdm

from .models import Organisation, RelatedOrganisation


class SearchWithTemplate(Search):

    def execute(self, ignore_cache=False, params=None):
        """
        Execute the search and return an instance of ``Response`` wrapping all
        the data.
        :arg ignore_cache: if set to ``True``, consecutive calls will hit
            ES, while cached result will be ignored. Defaults to `False`
        """
        if ignore_cache or not hasattr(self, '_response'):
            es = get_connection(self._using)

            if params:
                self._response = self._response_class(
                    self,
                    es.search_template(
                        index=self._index,
                        body={
                            "source": self.to_dict(),
                            "params": params,
                        },
                        **self._params
                    )
                )
            else:
                self._response = self._response_class(
                    self,
                    es.search(
                        index=self._index,
                        body=self.to_dict(),
                        **self._params
                    )
                )
        return self._response


class DSEPaginator(Paginator):
    """
    Override Django's built-in Paginator class to take in a count/total number of items;
    Elasticsearch provides the total as a part of the query results, so we can minimize hits.
    """

    def __init__(self, *args, **kwargs):
        super(DSEPaginator, self).__init__(*args, **kwargs)
        self._count = self.object_list.hits.total

    def page(self, number):
        # this is overridden to prevent any slicing of the object_list - Elasticsearch has
        # returned the sliced data already.
        number = self.validate_number(number)
        return Page(self.object_list, number, self)


@registry.register_document
class FullOrganisation(Document):

    org_id = fields.KeywordField()
    complete_names = fields.CompletionField(contexts=[
        {
            "name": "organisationType",
            "type": "category",
            "path": "organisationType"
        }
    ])
    orgIDs = fields.KeywordField()
    alternateName = fields.TextField()
    organisationType = fields.KeywordField()
    organisationTypePrimary = fields.KeywordField()
    source = fields.KeywordField()
    domain = fields.KeywordField()
    latestIncome = fields.IntegerField()

    @classmethod
    def search(cls, using=None, index=None):
        return SearchWithTemplate(
            using=cls._get_using(using),
            index=cls._default_index(index),
            doc_type=[cls],
            model=cls.django.model
        )
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

    def prepare_organisationTypePrimary(self, instance):
        return instance.organisationTypePrimary.slug

    def prepare_domain(self, instance):
        return instance.domain

    def prepare_latestIncome(self, instance):
        return instance.latestIncome

    def prepare_source(self, instance):
        return [s.id for s in instance.sources]

    def prepare_org_id(self, instance):
        return str(instance.org_id)

    def get_queryset(self):
        """
        Return the queryset that should be indexed by this doc type.
        """
        sql = """
        select distinct on ("linked_orgs") "id", "org_id", "linked_orgs"
        from ftc_organisation
        """

        return self.django.model.objects.raw(sql)

    def get_indexing_queryset(self):
        """
        Build queryset (iterator) for use by indexing.
        """
        qs = self.get_queryset()
        for o in tqdm.tqdm(qs):
            if o:
                yield RelatedOrganisation.from_orgid(o.linked_orgs[0])

    def bulk(self, actions, **kwargs):
        if self.django.queryset_pagination and 'chunk_size' not in kwargs:
            kwargs['chunk_size'] = self.django.queryset_pagination
        return bulk(client=self._get_connection(), actions=actions, **kwargs)

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
        queryset_pagination = 3000

    def get_related_orgs(self):
        return Organisation.objects.filter(org_id__in=self.orgIDs)
