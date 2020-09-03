import requests_html
from django.core.management.base import BaseCommand

from charity.feeds import CCEW_DATA_URL
from charity.models import CcewDataFile


class Command(BaseCommand):

    def handle(self, *args, **options):
        session = requests_html.HTMLSession()
        r = session.get(CCEW_DATA_URL)
        for d in r.html.find("blockquote.download"):
            for p in d.find("p"):
                if "Charity register extract" in p.text:
                    links = p.absolute_links
                    for link in links:
                        f, created = CcewDataFile.objects.update_or_create(
                            title=d.find("h4", first=True).text,
                            defaults=dict(
                                url=link,
                                description=p.text
                            )
                        )
                        print("{} ({})".format(f, "created" if created else "updated"))
