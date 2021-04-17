import datetime

from django.db import models


class Source(models.Model):
    id = models.CharField(max_length=200, unique=True, db_index=True, primary_key=True)
    data = models.JSONField()

    @property
    def title(self):
        return self.data.get("title")

    @property
    def publisher(self):
        return self.data.get("publisher", {}).get("name")

    @property
    def slug(self):
        return self.id

    @property
    def modified(self):
        return datetime.datetime.fromisoformat(self.data.get("modified"))

    def __str__(self):
        return self.publisher + " (" + self.title + ")"
