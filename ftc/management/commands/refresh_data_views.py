from ftc.management.commands._base_scraper import SQLRunner


class Command(SQLRunner):
    help = "Refresh charity data view"
    name = "refresh_charity_data"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_sql = {
            "Refresh charity data view": """
            REFRESH MATERIALIZED VIEW superhighways_london_organisations_view;
            """
        }
