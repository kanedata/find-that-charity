from unittest import TestCase

from ftc.models import Organisation


class TestOrganisation(TestCase):
    def test_organisation_url(self):
        urls = (
            # original url, cleanUrl, displayUrl
            ("university.ac.uk", "http://university.ac.uk", "university.ac.uk"),
            (
                "http://www.charity.org.uk/",
                "http://www.charity.org.uk/",
                "charity.org.uk",
            ),
            (
                "https://www.charity.org.uk/",
                "https://www.charity.org.uk/",
                "charity.org.uk",
            ),
            ("https://charity.org.uk/", "https://charity.org.uk/", "charity.org.uk"),
            ("//charity.org.uk/", "//charity.org.uk/", "charity.org.uk"),
            (
                "https://www.charity.org.uk/www.html",
                "https://www.charity.org.uk/www.html",
                "charity.org.uk/www.html",
            ),
            (
                "www.charity.org.uk/www.html",
                "http://www.charity.org.uk/www.html",
                "charity.org.uk/www.html",
            ),
        )
        for u in urls:
            o = Organisation(url=u[0])
            assert o.cleanUrl == u[1]
            assert o.displayUrl == u[2]
