from ftc.management.commands._base_scraper import SQLRunner
from ftc.models import OrgidScheme

UPDATE_ORGIDS_SQL = {
    "update domains": """
    UPDATE ftc_organisation
    SET domain = lower(substring(email from '@(.*)$'))
    WHERE lower(substring(email from '@(.*)$')) not in (
        'gmail.com', 'hotmail.com', 'btinternet.com',
        'hotmail.co.uk', 'yahoo.co.uk', 'outlook.com',
        'aol.com', 'btconnect.com', 'yahoo.com',
        'googlemail.com', 'ntlworld.com',
        'talktalk.net',
        'sky.com',
        'live.co.uk',
        'ntlworld.com',
        'tiscali.co.uk',
        'icloud.com',
        'btopenworld.com',
        'blueyonder.co.uk',
        'virginmedia.com',
        'nhs.net',
        'me.com',
        'msn.com',
        'talk21.com',
        'aol.co.uk',
        'mail.com',
        'live.com',
        'virgin.net',
        'ymail.com',
        'mac.com',
        'waitrose.com',
        'gmail.co.uk'
    )
    """,
    "Update priorities field": """
    WITH priorities AS (SELECT ARRAY[{}]::varchar[] AS prefixes)
    UPDATE ftc_organisation o
    SET priority = array[
        case when active then 0 else 1 end,
        coalesce(array_position(priorities.prefixes, org_id_scheme_id), 99),
        coalesce(extract(epoch from o."dateRegistered"), 0)
    ]
    from priorities
    """.format(",".join([f"'{p}'" for p in OrgidScheme.PRIORITIES])),
    "Add linked orgIDs": """
        UPDATE ftc_organisation o
        SET "linked_orgs" = a.linked_orgs
        FROM (
            WITH RECURSIVE a AS (
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
            ),
            search_graph(org_id_a, org_id_b) AS (
                SELECT a.org_id_a, a.org_id_b
                FROM a
                UNION
                SELECT sg.org_id_a, a.org_id_b
                FROM a
                    INNER JOIN search_graph sg
                        ON a.org_id_a = sg.org_id_b
            )
            SELECT org_id_a AS "org_id",
                array_agg(org_id_b ORDER BY o.priority, org_id_b ASC NULLS LAST) AS linked_orgs
            FROM search_graph
                LEFT OUTER JOIN ftc_organisation o
                    ON search_graph.org_id_b = o.org_id
            GROUP BY org_id_a
        ) AS a
        WHERE a.org_id = o.org_id;
    """,
    "Add verified linked orgIDs": """
        UPDATE ftc_organisation o
        SET "linked_orgs_verified" = a.linked_orgs_verified
        FROM (
            WITH RECURSIVE official_sources AS (
                SELECT distinct source_id
                FROM ftc_organisation 
            ),
            official_links AS (
                SELECT fo.*
                FROM ftc_organisationlink fo
                INNER JOIN official_sources s
                    ON fo.source_id = s.source_id
            ),
            a AS (
                SELECT official_links.org_id_a,
                    official_links.org_id_b
                FROM official_links
                UNION
                SELECT official_links.org_id_b AS org_id_a,
                    official_links.org_id_a AS org_id_b
                FROM official_links
                UNION
                SELECT official_links.org_id_a,
                    official_links.org_id_a AS org_id_b
                FROM official_links
                UNION
                SELECT official_links.org_id_b AS org_id_a,
                    official_links.org_id_b
                FROM official_links
            ),
            search_graph(org_id_a, org_id_b) AS (
                SELECT a.org_id_a, a.org_id_b
                FROM a
                UNION
                SELECT sg.org_id_a, a.org_id_b
                FROM a
                    INNER JOIN search_graph sg
                        ON a.org_id_a = sg.org_id_b
            )
            SELECT org_id_a AS "org_id",
                array_agg(org_id_b ORDER BY o.priority, org_id_b ASC NULLS LAST) AS linked_orgs_verified
            FROM search_graph
                LEFT OUTER JOIN ftc_organisation o
                    ON search_graph.org_id_b = o.org_id
            GROUP BY org_id_a
        ) AS a
        WHERE a.org_id = o.org_id
    """,
    "Add missing orgIDs": """
        UPDATE ftc_organisation
        SET linked_orgs = string_to_array(org_id, '')
        WHERE linked_orgs IS NULL
    """,
    "Add missing orgIDs (linked orgs verified)": """
        UPDATE ftc_organisation
        SET linked_orgs_verified = string_to_array(org_id, '')
        WHERE linked_orgs_verified IS NULL
    """,
    "Add names from grant data": """
        INSERT INTO charity_charityname ("charity_id", "name", "name_type")
        SELECT "recipientOrganization_id" AS "charity_id",
            "recipientOrganization_name" AS "name",
            'Grant' AS "name_type"
        FROM other_data_grant g 
            INNER JOIN charity_charity c
                ON g."recipientOrganization_id" = c.id
        GROUP BY 1, 2
        ON CONFLICT (charity_id, name) DO NOTHING
    """,
}


class Command(SQLRunner):
    help = "Find linked orgIDs"
    name = "update_orgids"
    models_to_delete = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_sql = UPDATE_ORGIDS_SQL

    def run_scraper(self, *args, **options):
        # close the spider
        self.close_spider()
        self.logger.info("Spider finished")
