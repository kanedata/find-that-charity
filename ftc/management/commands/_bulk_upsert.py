from typing import List

from django.db import connections
from django.db.models import Model
from psycopg2.extras import execute_values


# from https://gist.github.com/aisayko/dcacd546bcb17a740dec703de6b2377e
def bulk_upsert(model: Model, fields: List[str], values: List[List], by: List[str]):
    """
    Return the tuple of (inserted, updated) ids
    """

    def comma_separated(items):
        return ", ".join([f'"{i}"' for i in items])

    if values:
        stmt = """
            INSERT INTO "{table}" ({fields_str})
            VALUES %s
            ON CONFLICT ({by})
            DO
            UPDATE SET ({set_fields})=({set_values})
        """
        set_fields = comma_separated([f for f in fields if f not in by])
        set_values = ", ".join([f'EXCLUDED."{f}"' for f in fields if f not in by])

        formatted_sql = stmt.format(
            table=model._meta.db_table,
            fields_str=comma_separated(fields),
            by=comma_separated(by),
            set_fields=set_fields,
            set_values=set_values,
        )

        with connections["data"].cursor() as cursor:
            execute_values(cursor, formatted_sql, values)
