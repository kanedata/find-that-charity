import requests
from django.core.management.base import BaseCommand

from ftc.models import OrgidScheme


class Command(BaseCommand):

    start_url = 'http://org-id.guide/download.json'

    def handle(self, *args, **options):
        print("Fetching url")
        r = requests.get(self.start_url)
        
        print("iterating records")
        count = 0
        for record in r.json()['lists']:
            obj, created = OrgidScheme.objects.get_or_create(
                code=record['code'],
                defaults={'data': record},
            )
            count += 1
        print("Saved {:,.0f} records".format(count))
