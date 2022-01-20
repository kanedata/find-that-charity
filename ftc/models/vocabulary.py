from django.db import models
from django.utils.text import slugify
from markdownx.models import MarkdownxField


class Vocabulary(models.Model):
    slug = models.SlugField(max_length=200, unique=True, null=True)
    title = models.CharField(max_length=255, db_index=True, unique=True)
    description = MarkdownxField(blank=True, null=True)
    single = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Vocabulary, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Vocabulary"
        verbose_name_plural = "Vocabularies"


class VocabularyEntries(models.Model):
    vocabulary = models.ForeignKey(
        "Vocabulary", on_delete=models.CASCADE, related_name="entries"
    )
    code = models.CharField(max_length=500, db_index=True)
    title = models.CharField(max_length=500, db_index=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    current = models.BooleanField(default=True)

    class Meta:
        unique_together = (
            "vocabulary",
            "code",
        )
        verbose_name = "Vocabulary Entry"
        verbose_name_plural = "Vocabulary Entries"

    def __str__(self):
        if slugify(self.title) == slugify(self.code):
            return self.title
        return "[{}] {}".format(self.code, self.title)
