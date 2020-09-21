from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed

from ftc.models import Scrape


class ScrapesFeedRSS(Feed):
    title = "Find that Charity failed scrapes"
    link = '/admin/ftc/scrape/'
    description = "RSS feed showing failed scraping from Find that Charity."

    def items(self):
        return Scrape.objects.filter(status__in=[Scrape.ScrapeStatus.ERRORS, Scrape.ScrapeStatus.FAILED]).order_by("-start_time")[:10]

    def item_title(self, item):
        return "SCRAPER FAILED: " + item.spider

    def item_description(self, item):
        return "<pre>" + item.log + "</pre>"

    def item_pubdate(self, item):
        return item.start_time

    def item_link(self, item):
        return '/admin/ftc/scrape/{}/change/'.format(item.id)


class ScrapesFeedAtom(ScrapesFeedRSS):
    feed_type = Atom1Feed
    subtitle = ScrapesFeedRSS.description
