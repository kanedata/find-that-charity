import tweepy
from django.conf import settings
from django.core.management.base import BaseCommand

from charity.models import Charity
from findthatcharity.utils import to_titlecase
from ftc.documents import FullOrganisation
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
        q = FullOrganisation.search().from_dict(
            random_query(True, "registered-charity")
        )[0]
        result = q.execute()
        for r in result:
            return Charity.objects.get(id=r["org_id"])

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
            char["website"] = charity.web

        # correct common misformed URL in websites
        # @todo - make this a bit more robust
        if char["website"][0:4] != "http":
            char["website"] = "http://" + char["website"]

        # return the tweet format
        return "{title} [{regno}] {website}{income}".format(**char)

    def handle(self, *args, **options):
        charity = self.get_random_charity()
        self.stdout.write(self.style.SUCCESS("Random charity: {}".format(charity)))
        tweet_text = self.create_tweet_text(charity)
        self.stdout.write(self.style.SUCCESS("Tweet: {}".format(tweet_text)))

        # create the tweet
        self.create_api_client()
        self.client.create_tweet(
            text=tweet_text,
        )