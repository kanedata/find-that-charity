import logging

from django.conf import settings
from django.core import management

from ftc.documents import FullOrganisation
from ftc.management.commands._base_scraper import BaseScraper

ALIAS = "full-organisation-load"
PATTERN = ALIAS + "-*"
REQUEST_TIMEOUT = 3600


class FullOrganisationAlias(FullOrganisation):
    def __init__(self, alias=None, *args, **kwargs):
        super(FullOrganisationAlias, self).__init__(*args, **kwargs)
        if alias:
            self.alias_index = alias

    def _prepare_action(self, object_instance, action):
        result = super(FullOrganisationAlias, self)._prepare_action(
            object_instance, action
        )
        result["_index"] = self._get_index()
        return result

    def _get_index(self, index=None, required=True):
        if hasattr(self, "alias_index"):
            return self.alias_index
        return super(FullOrganisationAlias, self)._get_index(index, required)


class Command(BaseScraper):
    help = "Add Organisations to elasticsearch index"
    name = "es_load"

    def add_arguments(self, parser):
        parser.add_argument(
            "--parallel",
            action="store_true",
            dest="parallel",
            help="Run populate/rebuild update multi threaded",
        )
        parser.add_argument(
            "--no-parallel",
            action="store_false",
            dest="parallel",
            help="Run populate/rebuild update single threaded",
        )
        parser.set_defaults(
            parallel=getattr(settings, "ELASTICSEARCH_DSL_PARALLEL", False)
        )
        parser.add_argument(
            "--no-count",
            action="store_false",
            default=True,
            dest="count",
            help="Do not include a total count in the summary log line",
        )

    def run_scraper(self, *args, **options):

        # setup logging to capture elasticsearch output
        self.logging_setup()

        # run the update_orgids scraper
        management.call_command("update_orgids")

        # run the postgres version
        # Organisation.objects.update(search_vector=SearchVector('name', weight="A") + SearchVector("alternateName", weight="B"))

        # create new index
        next_index = PATTERN.replace("*", str(self.scrape.id))
        self.logger.info("New index name: {}".format(next_index))

        # create an instance of the doc with the right index
        doc = FullOrganisationAlias(alias=next_index)

        # get the low level connection
        es = doc._get_connection()

        # create an index template
        self.logger.info("Creating index template")
        index_template = doc._index.as_template(ALIAS, PATTERN)
        index_template.save()
        self.logger.info("Creating index template - done")

        # create new index, it will use the settings from the template
        self.logger.info("Creating new index")
        es.indices.create(index=next_index)
        self.logger.info("Creating new index - done")

        # populate the index (bulk)
        parallel = options["parallel"]
        self.logger.info(
            "Indexing {} '{}' objects {}".format(
                doc.get_queryset().count() if options["count"] else "all",
                doc.django.model.__name__,
                "(parallel)" if parallel else "",
            )
        )
        qs = doc.get_indexing_queryset()
        result = doc.update(qs, parallel=parallel, request_timeout=REQUEST_TIMEOUT)
        self.scrape.items = result[0]
        self.scrape.results = {
            "records_indexed": result[0],
            "errors": result[1],
        }
        self.logger.info("Indexing objects - done")

        if not result[0] or result[1]:
            raise Exception("Organisations were not indexed")

        # alias the index to the proper name
        self.logger.info("Reset aliases")
        es.indices.update_aliases(
            body={
                "actions": [
                    {"remove": {"alias": doc._index._name, "index": PATTERN}},
                    {"add": {"alias": doc._index._name, "index": next_index}},
                ]
            }
        )
        self.logger.info("Reset aliases - done")

        # delete any previous indexes
        self.logger.info("Delete previous indices")
        for index in es.indices.get("*"):
            if index != next_index:
                es.indices.delete(index=index)
        self.logger.info("Delete previous indices - done")

        self.scrape_logger.teardown()

    def logging_setup(self):

        # hook into elasticsearch logger too
        es_logger = logging.getLogger("elasticsearch")
        es_logger.addHandler(self.scrape_logger)

        # hook into the update_orgids logger
        uo_logger = logging.getLogger("ftc.management.commands.update_orgids")
        uo_logger.addHandler(self.scrape_logger)
