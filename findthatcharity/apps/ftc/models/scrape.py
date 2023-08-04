from django.db import models


class Scrape(models.Model):
    class ScrapeStatus(models.TextChoices):
        RUNNING = "running", "In progress"
        SUCCESS = "success", "Finished successfully"
        ERRORS = "errors", "Finished with errors"
        FAILED = "failed", "Failed to complete"

    spider = models.CharField(max_length=200)
    result = models.JSONField(null=True, blank=True, editable=False)
    start_time = models.DateTimeField(auto_now_add=True, editable=False)
    finish_time = models.DateTimeField(
        auto_now=True, null=True, blank=True, editable=False
    )
    log = models.TextField(null=True, blank=True, editable=False)
    items = models.IntegerField(default=0, editable=False)
    errors = models.IntegerField(default=0, editable=False)
    status = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=ScrapeStatus.choices,
        editable=False,
    )

    def __str__(self):
        return "{} [{}] {:%Y-%m-%d %H:%M}".format(
            self.spider, self.status, self.start_time
        )
