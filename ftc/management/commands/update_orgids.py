from ftc.management.commands._base_scraper import SQLRunner
from ftc.models import OrgidScheme

UPDATE_ORGIDS_SQL = {
    "update domains": """
    update ftc_organisation
    set domain = lower(substring(email from '@(.*)$'))
    where lower(substring(email from '@(.*)$')) not in (
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
    "Add linked orgIDs": """
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
    "Update priorities field": """
    with priorities as (select ARRAY[{}]::varchar[] as prefixes)
    update ftc_organisation o
    set priority = array[
        case when active then 0 else 1 end,
        coalesce(array_position(priorities.prefixes, org_id_scheme_id), 99),
        coalesce(extract(epoch from o."dateRegistered"), 0)
    ]
    from priorities;
    """.format(
        ",".join([f"'{p}'" for p in OrgidScheme.PRIORITIES])
    ),
    "Add names from grant data": """
        insert into charity_charityname ("charity_id", "name", "name_type")
        select "recipientOrganization_id" as "charity_id",
            "recipientOrganization_name" as "name",
            'Grant' as "name_type"
        from other_data_grant g 
            inner join charity_charity c
                on g."recipientOrganization_id" = c.id
        group by 1, 2
        on conflict (charity_id, name) do nothing
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
