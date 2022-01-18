from django.db import models
from django.utils.text import slugify


class Vocabulary(models.Model):
    title = models.CharField(max_length=255, db_index=True, unique=True)
    single = models.BooleanField()

    def __str__(self):
        return self.title

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
