import yaml
from django.utils import timezone

from charity.models import CharityRaw
from ftc.management.commands._base_scraper import HTMLScraper


class Command(HTMLScraper):
    name = "ccni_scrape"
    base_url = (
        "https://www.charitycommissionni.org.uk/charity-details/?regid={}&subid=0"
    )

    def run_scraper(self, *args, **options):
        # set up cache if we're caching
        self.set_session(options.get("cache"))

        regnos = ["103672", "104956", "100203"]
        for r in regnos:
            data = self.scrape_charity(r)
            data["scraped"] = timezone.now()
            c = CharityRaw(
                org_id="GB-NIC-{}".format(r),
                spider=self.name,
                scrape=self.scrape,
                data=data,
            )
            c.save()
            print(c)

    def scrape_charity(self, regno):
        r = self.session.get(self.base_url.format(regno))

        details = {}

        # textual details first
        for b in r.html.find(".pcg-charity-details__block"):
            value = "".join([p.text for p in b.find("p")])
            key = b.find("h3", first=True).text
            if value:
                details[key] = value

            if key == "Trustee board":
                details[key] = [td.text for td in b.find("td")]

        # financial details from pie chart
        for s in r.html.find("script"):
            if "charityFinancials" in s.text:
                t = s.text.replace("&#13;", "").strip()
                t = t.replace("$(function () { var charityFinancials = ", "")
                t = t[: t.find("; $.pcg.frontend.pieChart")]
                data = yaml.safe_load(t)
                entries = {}
                for e in data["entries"]:
                    label = e["label"][: e["label"].find(":")]
                    entries[label] = e["value"]
                details[data["title"]] = entries

        # number of employees, etc
        for f in r.html.find(".pcg-charity-details__fact"):
            key = f.find(".pcg-charity-details__purpose", first=True).text
            value = int(
                f.find(".pcg-charity-details__amount", first=True).text.replace(",", "")
            )
            details[key] = value

        # get locations
        locations = [li.text for li in r.html.find("#operations li")]
        if locations:
            details["locations"] = locations

        return details
