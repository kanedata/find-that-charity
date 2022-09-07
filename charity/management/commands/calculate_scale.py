import tqdm
from django.utils.text import slugify

from ftc.management.commands._base_scraper import BaseScraper
from ftc.models import OrganisationClassification, Vocabulary, VocabularyEntries

BASE_SQL = """
with locations as (
    select org_id,
        "locationType",
        geo_iso,
        case when geo_ctry like '%9999999' then null else geo_ctry end as geo_ctry,
        case when geo_rgn like '%9999999' then null else geo_rgn end as geo_rgn,
        coalesce(
            case when geo_laua like '%9999999' then null else geo_laua end,
            case when geo_cty like '%9999999' then null else geo_cty end
        ) as geo_laua
    from ftc_organisationlocation
)
select org_id,
    count(distinct geo_iso) filter (where geo_iso != 'GB') as overseas,
    count(distinct geo_ctry) filter (where geo_ctry is not null) as uk_countries,
    count(distinct geo_rgn) filter (where geo_rgn is not null) as uk_regions,
    count(distinct geo_laua) filter (where geo_laua is not null) as uk_las
from locations
where "locationType" in ('AOO', 'SITE')
group by org_id
"""
LOCAL = "Local"
REGIONAL = "Regional"
NATIONAL = "National"
OVERSEAS = "Overseas"
NATIONAL_AND_OVERSEAS = "National and Overseas"
SCALE_OPTIONS = [
    LOCAL,
    REGIONAL,
    NATIONAL,
    OVERSEAS,
    NATIONAL_AND_OVERSEAS,
]


class Command(BaseScraper):
    name = "calculate_scale"
    source = {
        "title": "Calculate the scale of operation",
        "description": "A calculation of the scale of the organisation's operation, based on locations it has provided to the Charity Commission",
        "identifier": "calculate_scale",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Find that Charity",
            "website": "https://github.com/drkane/charity-lookups",
        },
    }
    models_to_delete = [
        OrganisationClassification,
    ]

    def run_scraper(self, *args, **options):
        # save any sources
        self.logger.info("saving sources")
        self.save_sources()
        self.logger.info("sources saved")

        self.logger.info("Set up vocabulary")
        v, _ = Vocabulary.objects.update_or_create(
            slug="scale",
            title="Scale of operation",
            defaults=dict(single=False),
        )
        self.scales = {}
        for s in SCALE_OPTIONS:
            ve, _ = VocabularyEntries.objects.update_or_create(
                code=slugify(s), vocabulary=v, defaults={"title": s, "current": True}
            )
            self.scales[s] = ve

        self.logger.info("Calculating scale")
        self.cursor.execute(BASE_SQL)
        columns = [col[0] for col in self.cursor.description]
        for row in tqdm.tqdm(self.cursor):
            row = dict(zip(columns, row))
            row["scale"] = self.calculate_scale(row)
            if row["scale"]:
                self.add_record(
                    OrganisationClassification,
                    dict(
                        org_id=row["org_id"],
                        spider=self.name,
                        scrape=self.scrape,
                        source=self.source,
                        vocabulary=self.scales[row["scale"]],
                    ),
                )

        # close the spider
        self.close_spider()
        self.logger.info("Spider finished")

    def calculate_scale(self, row):
        row["total"] = (
            row["overseas"] + row["uk_countries"] + row["uk_regions"] + row["uk_las"]
        )

        # easy local charities - one local authority
        if (
            (row["uk_las"] == 1)
            and (row["uk_countries"] == 1)
            and (row["overseas"] == 0)
        ):
            return LOCAL

        # easy national charities - one+ country in UK
        if (row["uk_countries"] > 0) and (row["uk_countries"] == row["total"]):
            return NATIONAL

        # easy international charities - one+ overseas country only
        if (row["overseas"] > 0) and (row["overseas"] == row["total"]):
            return OVERSEAS

        # easy regional charities - one+ region only
        if (
            (row["uk_regions"] > 0)
            and (row["uk_countries"] == 1)
            and (row["overseas"] == 0)
        ):
            return REGIONAL

        # national and overseas
        if (row["overseas"] > 0) and (row["total"] > row["overseas"]):
            return NATIONAL_AND_OVERSEAS

        # let's call between 2-10 local authorities "regional"
        if (row["uk_las"] > 1) and (row["uk_las"] < 10):
            return REGIONAL

        # let's call more than 10 local authorities "national"
        if row["uk_las"] > 10:
            return NATIONAL

        # anything regional with no countries is regional
        if (
            (row["uk_regions"] > 1)
            and (row["uk_countries"] <= 1)
            and (row["overseas"] == 0)
        ):
            return REGIONAL

        # anything with a country with no countries overseas is national
        if (row["uk_countries"] > 1) and (row["overseas"] == 0):
            return NATIONAL

        return None
