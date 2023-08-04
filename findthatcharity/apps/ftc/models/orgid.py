from django.db import models


class Orgid(str):
    def __new__(cls, content):
        instance = super().__new__(cls, content)
        instance._split_orgid(content)
        return instance

    def _split_orgid(self, value):
        self.scheme = None
        self.id = value
        if value is None:
            return
        if value.upper().startswith("360G-"):
            self.scheme = "360G"
            self.id = value[5:]
            return

        split_orgid = value.split("-", maxsplit=3)
        if len(split_orgid) > 2:
            self.scheme = "-".join(split_orgid[:2])
            self.id = "-".join(split_orgid[2:])


class OrgidField(models.CharField):
    description = "An orgid based on the format here: http://org-id.guide/about"

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 200
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return Orgid(value)

    def to_python(self, value):
        if isinstance(value, Orgid):
            return value

        if value is None:
            return value

        return Orgid(value)
