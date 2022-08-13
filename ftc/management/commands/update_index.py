from itertools import groupby

import tqdm
from django.contrib.postgres.search import SearchVector

from ftc.management.commands._base_scraper import BaseScraper
from ftc.models import Organisation, OrganisationGroup


class Command(BaseScraper):
    help = "Update global organisation index"
    name = "update_index"
    models_to_delete = [OrganisationGroup]

    def run_scraper(self, *args, **options):
        # Create organisation group records
        qs = Organisation.objects.filter(linked_orgs__isnull=False).order_by(
            "linked_orgs"
        )
        for k, orgs in groupby(
            tqdm.tqdm(
                qs.iterator(), total=qs.count(), position=0, smoothing=0.1, leave=True
            ),
            key=lambda o: o.linked_orgs,
        ):
            org_group = OrganisationGroup.from_orgs(orgs)
            org_group.scrape = self.scrape
            org_group.spider = self.name
            self.add_record(OrganisationGroup, org_group)

        # close the spider
        self.close_spider()
        self.logger.info("Spider finished.")

    def execute_sql_statements(self, sqls):
        self.logger.info("Update search vectors")
        OrganisationGroup.objects.update(
            search_vector=SearchVector("name", weight="A")
            + SearchVector("alternateName", weight="B")
        )
        self.logger.info("Updated search vectors")
