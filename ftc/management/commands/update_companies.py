from charity_django.companies.models import SICCode

from ftc.management.commands._base_scraper import SQLRunner
from ftc.models import Vocabulary, VocabularyEntries

UPDATE_ORGIDS_SQL = {
    "Add companies": """
with pn as (
    select "CompanyNumber",
        array_agg("CompanyName") as "alternateName"
    from companies_previousname
    group by "CompanyNumber"
),
c as (
    select *,
        'GB-COH-' || c."CompanyNumber" as "org_id",
        'GB-COH-' || TRIM(LEADING '0' FROM c."CompanyNumber") as "org_id_alt",
        case
            when "CompanyCategory" like 'private-limited-guarant-nsc%%' then 'company-limited-by-guarantee'
            when "CompanyCategory" = 'private-unlimited-nsc' then 'private-unlimited'
            when "CompanyCategory" = 'royal-charter' then 'royal-charter-company'
            when "CompanyCategory" = 'registered-society-non-jurisdictional' then 'registered-society'
            else "CompanyCategory"
        end as orgtype
    from companies_company c
    where c."CompanyCategory" in (
            'private-limited-guarant-nsc-limited-exemption',
            'private-limited-guarant-nsc',
            'community-interest-company',
            'private-unlimited-nsc',
            'registered-society-non-jurisdictional',
            'industrial-and-provident-society',
            'royal-charter',
            'charitable-incorporated-organisation',
            'scottish-charitable-incorporated-organisation'
        )
)
insert into ftc_organisation (
    "org_id",
    "orgIDs",
    "name",
    "alternateName",
    "companyNumber",
    "streetAddress",
    "addressLocality",
    "addressRegion",
    "addressCountry",
    "postalCode",
    "dateRegistered",
    "dateRemoved",
    "active",
    "organisationType",
    "organisationTypePrimary_id",
    "dateModified",
    "scrape_id",
    "source_id",
    "spider",
    "org_id_scheme_id"
)
select c."org_id" as "org_id",
    CASE WHEN c."org_id" = c."org_id_alt" THEN array [c."org_id"] ELSE array [c."org_id", c."org_id_alt"] END as "orgIDs",
    c."CompanyName" as name,
    pn."alternateName" as "alternateName",
    c."CompanyNumber" as "companyNumber",
    NULLIF(concat_ws(
        ', ',
        NULLIF(c."RegAddress_CareOf", 'None'),
        NULLIF(c."RegAddress_POBox", 'None'),
        NULLIF(c."RegAddress_AddressLine1", 'None'),
        NULLIF(c."RegAddress_AddressLine2", 'None')
    ), '') as "streetAddress",
    NULLIF(c."RegAddress_PostTown", 'None') as "addressLocality",
    NULLIF(c."RegAddress_County", 'None') as "addressRegion",
    NULLIF(c."RegAddress_Country", 'None') as "addressCountry",
    NULLIF(c."RegAddress_PostCode", 'None') as "postalCode",
    c."IncorporationDate" as "dateRegistered",
    c."DissolutionDate" as "dateRemoved",
    case
        when c."DissolutionDate" is not null then false
        when c."CompanyStatus" in ('dissolved', 'inactive', 'converted-or-closed') then false
        when c.in_latest_update = false then false
        else true
    end as "active",
    array [c.orgtype, 'registered-company'] as "organisationType",
    c.orgtype as "organisationTypePrimary_id",
    c.last_updated as "dateModified",
    %(scrape_id)s as "scrape_id",
    %(spider_name)s as "source_id",
    %(source_id)s as "spider",
    'GB-COH' as "org_id_scheme_id"
from c
    left outer join pn on c."CompanyNumber" = pn."CompanyNumber";
    """,
    "Insert into organisation classification": """
    insert into ftc_organisationclassification as ca (org_id, spider, scrape_id, source_id, vocabulary_id )
    select c.org_id,
        %(spider_name)s as "spider",
        %(scrape_id)s as "scrape_id",
        %(source_id)s as "source_id",
        ve.id
    from (
        select CONCAT('GB-COH-', "CompanyNumber") as org_id,
            cast(code as varchar) as "code"
        from companies_companysiccode
    ) as c
        inner join ftc_vocabularyentries ve
            on c.code = ve.code
        inner join ftc_vocabulary v
            on ve.vocabulary_id = v.id
        inner join ftc_organisation o
            on c.org_id = o.org_id
    where v.slug like 'ch_sic';
    """,
    "Delete existing organisation classification": """
    delete from ftc_organisationclassification fo
    where source_id = %(source_id)s
        and spider = %(spider_name)s
        and scrape_id != %(scrape_id)s;
    """,
}


class Command(SQLRunner):
    help = "Update companies data"
    name = "companies"
    source = {
        "title": "Free Company Data Product",
        "description": "The Free Company Data Product is a downloadable data snapshot containing \
            basic company data of live companies on the register. This snapshot is provided as \
            ZIP files containing data in CSV format and is split into multiple files for ease of \
            downloading.",
        "identifier": "companies",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Companies House",
            "website": "https://www.gov.uk/government/organisations/companies-house",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "http://download.companieshouse.gov.uk/en_output.html",
                "title": "Company data as multiple files",
            }
        ],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_sql = UPDATE_ORGIDS_SQL

    def run_scraper(self, *args, **options):
        # save any sources
        self.logger.info("saving sources")
        self.save_sources()
        self.logger.info("sources saved")

        # create the classification vocabulary
        self.logger.info("Creating or updating vocabulary 'Companies House SIC Codes'")
        vocab = Vocabulary.objects.update_or_create(
            slug="ch_sic",
            defaults=dict(title="Companies House SIC Codes", single=False),
        )[0]
        sic_codes_total = 0
        sic_codes_created = 0
        for code in SICCode.objects.all():
            _, created = VocabularyEntries.objects.update_or_create(
                vocabulary=vocab, code=code.code, defaults={"title": code.title}
            )
            if created:
                sic_codes_created += 1
            sic_codes_total += 1
        self.logger.info("Created vocabulary 'Companies House SIC Codes'")
        self.logger.info("Created %s entries", sic_codes_created)
        self.logger.info("Total %s entries", sic_codes_total)

        # close the spider
        self.close_spider()
        self.logger.info("Spider finished")
