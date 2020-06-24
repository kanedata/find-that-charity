from django.utils.feedgenerator import Atom1Feed
from django.contrib.syndication.views import Feed
from django.urls import reverse
from requests_html import HTMLSession

from charity.models import CcewDataFile

CCEW_DATA_URL = "http://data.charitycommission.gov.uk/"

def fetch_ccew_data():
    session = HTMLSession()
    r = session.get(CCEW_DATA_URL)
    for d in r.html.find(".cc-postcontent blockquote"):
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


class CcewDataFeedRSS(Feed):
    title = "Charity data download"
    link = CCEW_DATA_URL
    description = "RSS feed for updates to the Data download service provided by the Charity Commission for registered charities in England and Wales."

    def items(self):
        fetch_ccew_data()
        return CcewDataFile.objects.order_by('-first_added')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_pubdate(self, item):
        return item.first_added


class CcewDataFeedAtom(CcewDataFeedRSS):
    feed_type = Atom1Feed
    subtitle = CcewDataFeedRSS.description
