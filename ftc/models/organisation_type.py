from django.db import models
from django.utils.text import slugify


class OrganisationType(models.Model):
    slug = models.SlugField(max_length=255, editable=False, primary_key=True)
    title = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        value = self.title
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)

    KEY_TYPES = [
        "registered-charity",
        "registered-charity-england-and-wales",
        "registered-charity-scotland",
        "registered-charity-northern-ireland",
        "registered-company",
        # "company limited by guarantee",
        "charitable-incorporated-organisation",
        "education-institution",
        "community-interest-company",
        "health-organisation",
        "registered-society",
        "community-amateur-sports-club",
        "registered-provider-of-social-housing",
        "government-organisation",
        "local-authority",
        "university",
        "church",
    ]

    def is_keytype(self):
        return self.slug in self.KEY_TYPES

    def __str__(self):
        return self.title
