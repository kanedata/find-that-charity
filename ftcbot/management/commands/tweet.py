import requests
import tweepy
from django.conf import settings
from django.core.management.base import BaseCommand

from charity.models import Charity
from findthatcharity.utils import to_titlecase
from ftc.documents import OrganisationGroup
from ftc.models.organisation import EXTERNAL_LINKS
from ftc.query import random_query
from other_data.models import WikiDataItem


class Command(BaseCommand):
    help = "Tweet a random charity"

    def create_api_client(self):
        self.client = tweepy.Client(
            consumer_key=settings.TWITTER_CONSUMER_KEY,
            consumer_secret=settings.TWITTER_CONSUMER_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
        )

    def get_random_charity(self):
        q = OrganisationGroup.search().from_dict(
            random_query(True, "registered-charity")
        )[:100]
        result = q.execute()
        for r in result:
            try:
                return Charity.objects.get(id=r["org_id"])
            except Charity.DoesNotExist:
                pass

    def get_twitter_id(self, charity):
        wikidata = WikiDataItem.objects.filter(org_id=charity.id).first()
        if wikidata:
            return wikidata.twitter

    def create_tweet_text(self, charity):
        char = {
            "title": to_titlecase(charity.name),
            "regno": charity.charity_number,
            "income": "",
            "website": "",
        }

        twitter_id = self.get_twitter_id(charity)
        if twitter_id:
            char["title"] += f" @{twitter_id}"

        if charity.id.startswith("GB-CHC"):
            char["website"] = EXTERNAL_LINKS["GB-CHC"][0][0].format(char["regno"])
        elif charity.id.startswith("GB-NIC"):
            char["website"] = EXTERNAL_LINKS["GB-NIC"][0][0].format(char["regno"])
        elif charity.id.startswith("GB-SC"):
            char["website"] = EXTERNAL_LINKS["GB-SC"][0][0].format(char["regno"])

        if charity.income:
            if charity.income > 1000000000:
                income = "{:,.1f}bn".format(charity.income / 1000000000)
            elif charity.income > 1000000:
                income = "{:,.1f}m".format(charity.income / 1000000)
            elif charity.income > 100000:
                income = "{:,.0f}k".format(charity.income / 1000)
            else:
                income = "{:,.0f}".format(charity.income)
            char["income"] = " (Latest income: £{})".format(income)

        # if a website exists then use it
        if charity.web and charity.web != "":
            # check for status code 200
            try:
                website = charity.web
                if not website.startswith("http"):
                    website = "http://" + website
                r = requests.get(website)
                r.raise_for_status()
                char["website"] = website
            except (requests.HTTPError, requests.exceptions.ConnectionError):
                pass

        # return the tweet format
        return "{title} {website} ({regno})".format(**char)

    def handle(self, *args, **options):
        charity = self.get_random_charity()
        self.stdout.write(self.style.SUCCESS("Random charity: {}".format(charity)))
        tweet_text = self.create_tweet_text(charity)
        self.stdout.write(self.style.SUCCESS("Tweet: {}".format(tweet_text)))

        # create the tweet
        if not settings.DEBUG:
            self.create_api_client()
            self.client.create_tweet(
                text=tweet_text,
            )
