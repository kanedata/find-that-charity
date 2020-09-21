from django.db import connection
from psycopg2.extras import execute_values


# from https://gist.github.com/aisayko/dcacd546bcb17a740dec703de6b2377e
def bulk_upsert(model, fields, values, by):
    """
    Return the tuple of (inserted, updated) ids
    """

    def comma_separated(items):
        return '"' + '", "'.join(items) + '"'

    if values:
        stmt = """
            INSERT INTO {table} ({fields_str})
            VALUES {values_placeholders}
            ON CONFLICT ({by})
            DO
            UPDATE SET ({set_fields})=({set_values})
        """
        set_fields = ", ".join([f for f in fields if f != by])
        set_values = ", ".join(["EXCLUDED.{0}".format(f) for f in fields if f != by])
        values_placeholders = ("%s, " * len(fields))[:-2]

        formatted_sql = stmt.format(
            table=model._meta.db_table,
            fields_str=comma_separated(fields),
            by=by,
            values_placeholders=values_placeholders,
            set_fields=set_fields,
            set_values=set_values,
        )

        with connection.cursor() as cursor:
            execute_values(cursor, formatted_sql, values)
