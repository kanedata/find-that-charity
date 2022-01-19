import csv
import io

import requests
from django.core.management.base import BaseCommand

from charity.models import AreaOfOperation
from ftc.models import Vocabulary, VocabularyEntries


class Command(BaseCommand):
    def handle(self, *args, **options):
        # fetch classifications
        self.fetch_cc_classifications()
        self.fetch_icnpo()
        self.fetch_aoo()

    def fetch_cc_classifications(self):
        print("Fetching CC classifications")
        ccew = "https://github.com/drkane/charity-lookups/raw/master/classification/ccew.csv"

        for f in ("theme", "beneficiaries", "activities"):
            v, _ = Vocabulary.objects.update_or_create(
                title="ccew_" + f, defaults=dict(single=False)
            )
            VocabularyEntries.objects.filter(vocabulary=v).update(current=False)

        for r in self.get_csv(ccew):
            v, _ = Vocabulary.objects.update_or_create(
                title="ccew_" + r["category"], defaults=dict(single=False)
            )
            VocabularyEntries.objects.update_or_create(
                code=r["code"],
                vocabulary=v,
                defaults={"title": r["name"], "current": True},
            )

    def fetch_icnpo(self):
        print("Fetching ICNPO")
        icnpo = "https://github.com/drkane/charity-lookups/raw/master/classification/icnpo.csv"
        v, _ = Vocabulary.objects.update_or_create(
            title="International Classification of Non Profit Organisations (ICNPO)",
            defaults=dict(single=False),
        )
        VocabularyEntries.objects.filter(vocabulary=v).update(current=False)
        icnpo_cats = []
        icnpo_group_names = set()
        for r in self.get_csv(icnpo):
            icnpo_cats.append(r)
            icnpo_group_names.add(r["icnpo_group"])

        icnpo_groups = {}
        for i in icnpo_group_names:
            ve, _ = VocabularyEntries.objects.update_or_create(
                code=i, vocabulary=v, defaults={"title": i, "current": True}
            )
            icnpo_groups[i] = ve

        for r in icnpo_cats:
            VocabularyEntries.objects.update_or_create(
                code=r["icnpo"],
                vocabulary=v,
                defaults={
                    "title": r["icnpo_desc"],
                    "parent": icnpo_groups[r["icnpo_group"]],
                    "current": True,
                },
            )

    # def fetch_ntee(self):
    #     ntee = 'https://github.com/drkane/charity-lookups/raw/master/classification/ntee.csv'

    def fetch_aoo(self):
        print("Fetching AOO lookups")
        aoo = "https://github.com/drkane/charity-lookups/raw/master/cc-aoo-gss-iso-new.csv"
        for r in self.get_csv(aoo):
            for k, v in r.items():
                if v == "":
                    r[k] = None
            ve, _ = AreaOfOperation.objects.update_or_create(
                aooname=r["geographic_area_description"],
                defaults={
                    "aoosort": r.get("geographic_area_description"),
                    "welsh": r.get("welsh") == "Y",
                    "GSS": r.get("GSS"),
                    "ISO3166_1": r.get("ISO3166-1"),
                    "ISO3166_1_3": r.get("ISO3166-1:3"),
                    "ISO3166_2_GB": r.get("ISO3166-2:GB"),
                    "ContinentCode": r.get("ContinentCode"),
                },
            )

    def get_csv(self, url, encoding="utf8"):
        response = requests.get(url)
        csv_text = response.content.decode(encoding)

        with io.StringIO(csv_text) as a:
            csvreader = csv.DictReader(a)
            for k, row in enumerate(csvreader):
                yield row
