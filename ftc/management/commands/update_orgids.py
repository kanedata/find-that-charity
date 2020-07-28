import logging

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):

    update_sql = {
        "Add linked orgIDS": """
            update ftc_organisation o
            set "linked_orgs" = a.linked_orgs
            from (
                WITH RECURSIVE search_graph(org_id_a, org_id_b) AS (
                        SELECT a.org_id_a, a.org_id_b
                        FROM (
                            SELECT ftc_organisationlink.org_id_a,
                                ftc_organisationlink.org_id_b
                            FROM ftc_organisationlink
                            UNION
                            SELECT ftc_organisationlink.org_id_b AS org_id_a,
                                ftc_organisationlink.org_id_a AS org_id_b
                            FROM ftc_organisationlink
                            UNION
                            SELECT ftc_organisationlink.org_id_a,
                                ftc_organisationlink.org_id_a AS org_id_b
                            FROM ftc_organisationlink
                            UNION
                            SELECT ftc_organisationlink.org_id_b AS org_id_a,
                                ftc_organisationlink.org_id_b
                            FROM ftc_organisationlink
                        ) a
                    union
                        SELECT sg.org_id_a, a.org_id_b
                        FROM (
                            SELECT ftc_organisationlink.org_id_a,
                                ftc_organisationlink.org_id_b
                            FROM ftc_organisationlink
                            UNION
                            SELECT ftc_organisationlink.org_id_b AS org_id_a,
                                ftc_organisationlink.org_id_a AS org_id_b
                            FROM ftc_organisationlink
                            UNION
                            SELECT ftc_organisationlink.org_id_a,
                                ftc_organisationlink.org_id_a AS org_id_b
                            FROM ftc_organisationlink
                            UNION
                            SELECT ftc_organisationlink.org_id_b AS org_id_a,
                                ftc_organisationlink.org_id_b
                            FROM ftc_organisationlink
                        ) a
                            inner JOIN search_graph sg
                                ON a.org_id_a = sg.org_id_b
                )
                SELECT org_id_a as "org_id",
                    array_agg(org_id_b ORDER BY org_id_b ASC) as linked_orgs
                FROM search_graph
                group by org_id_a
            ) as a
            where a.org_id = o.org_id;
        """,
        "Add missing orgIDs": """
            update ftc_organisation
            set linked_orgs = string_to_array(org_id, '')
            where linked_orgs is null;
        """,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            for name, sql in self.update_sql.items():
                self.logger.info("Starting SQL {}".format(name))
                cursor.execute(sql)
                self.logger.info("Finished SQL {}".format(name))
