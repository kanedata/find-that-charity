from typing import List

from django.db import NotSupportedError, connections
from django.db.models import Manager, Model
from django.db.models.constants import OnConflict
from django.db.models.query import QuerySet
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
            execute_values(
                cursor,
                formatted_sql,
                [tuple(row.get(f) for f in fields) for row in values],
            )


class BulkQuerySet(QuerySet):
    def _check_bulk_create_options(
        self, ignore_conflicts, update_conflicts, update_fields, unique_fields
    ):
        if ignore_conflicts and update_conflicts:
            raise ValueError(
                "ignore_conflicts and update_conflicts are mutually exclusive."
            )
        db_features = connections[self.db].features
        if ignore_conflicts:
            if not db_features.supports_ignore_conflicts:
                raise NotSupportedError(
                    "This database backend does not support ignoring conflicts."
                )
            return OnConflict.IGNORE
        elif update_conflicts:
            if not db_features.supports_update_conflicts:
                raise NotSupportedError(
                    "This database backend does not support updating conflicts."
                )
            if not update_fields:
                raise ValueError(
                    "Fields that will be updated when a row insertion fails "
                    "on conflicts must be provided."
                )
            if unique_fields and not db_features.supports_update_conflicts_with_target:
                raise NotSupportedError(
                    "This database backend does not support updating "
                    "conflicts with specifying unique fields that can trigger "
                    "the upsert."
                )
            if not unique_fields and db_features.supports_update_conflicts_with_target:
                raise ValueError(
                    "Unique fields that can trigger the upsert must be provided."
                )
            # Updating primary keys and non-concrete fields is forbidden.
            update_fields = [
                self.model._meta.get_field(name) if isinstance(name, str) else name
                for name in update_fields
                if name
            ]
            if any(not f.concrete or f.many_to_many for f in update_fields):
                raise ValueError(
                    "bulk_create() can only be used with concrete fields in "
                    "update_fields."
                )
            if any(f.primary_key for f in update_fields):
                raise ValueError(
                    "bulk_create() cannot be used with primary keys in update_fields."
                )
            if unique_fields:
                available_fields = {
                    f.get_attname_column()[1]: f for f in self.model._meta.get_fields()
                }
                # Primary key is allowed in unique_fields.
                unique_fields = [
                    available_fields.get(
                        name if isinstance(name, str) else (name.db_column or name.name)
                    )
                    for name in unique_fields
                    if name != "pk"
                ]
                if any(not f.concrete or f.many_to_many for f in unique_fields):
                    raise ValueError(
                        "bulk_create() can only be used with concrete fields "
                        "in unique_fields."
                    )
            return OnConflict.UPDATE
        return None


class BulkManager(Manager):
    def get_queryset(self):
        return BulkQuerySet(self.model)
