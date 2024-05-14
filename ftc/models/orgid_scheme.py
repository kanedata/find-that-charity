from django.db import models


class OrgidScheme(models.Model):
    PRIORITIES = [
        "GB-CHC",
        "GB-SC",
        "GB-NIC",
        "GB-WALEDU",
        "GB-EDU",
        "GB-LAE",
        "GB-PLA",
        "GB-LAS",
        "GB-LANI",
        "GB-GOR",
        "GB-MPR",
        "GB-COH",
    ]

    code = models.CharField(max_length=200, primary_key=True, db_index=True)
    data = models.JSONField()
    priority = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.code in self.PRIORITIES:
            self.priority = self.PRIORITIES.index(self.code)
        else:
            self.priority = len(self.PRIORITIES) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "{} - {}".format(self.code, self.data.get("name", {}).get("en"))
