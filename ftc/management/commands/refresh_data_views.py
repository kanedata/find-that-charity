from django.apps import apps
from django.conf import settings
from django.db import connections
from django_db_views.autodetector import ViewMigrationAutoDetector
from django_db_views.db_view import DBMaterializedView
from psycopg2 import sql

from ftc.management.commands._base_scraper import BaseScraper

DEFAULT_SHARED_MODELS = [
    "ftc.*",
    "charity.*",
    "geo.*",
    "other_data.*",
]


class Command(BaseScraper):
    help = "Refresh materialized data views"
    name = "refresh_data_views"

    def run_scraper(self, *args, **kwargs):
        self._refresh_views()
        self._ensure_readonly_users()

    def _check_view_exists(self, view, cursor=None):
        if cursor is None:
            with connections[settings.DATA_DB_ALIAS].cursor() as cursor:
                cursor.execute(sql.SQL("SELECT to_regclass(%s)"), [view._meta.db_table])
                result = cursor.fetchone()
                return result is not None and result[0] is not None
        else:
            cursor.execute(sql.SQL("SELECT to_regclass(%s)"), [view._meta.db_table])
            result = cursor.fetchone()
            return result is not None and result[0] is not None

    def _check_user_exists(self, user, cursor=None):
        if cursor is None:
            with connections[settings.DATA_DB_ALIAS].cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM pg_roles WHERE rolname = %(username)s",
                    {
                        "username": user,
                    },
                )
                result = cursor.fetchone()
                return result is not None
        else:
            cursor.execute(
                "SELECT 1 FROM pg_roles WHERE rolname = %(username)s",
                {
                    "username": user,
                },
            )
            result = cursor.fetchone()
            return result is not None

    def _refresh_views(self):
        views = ViewMigrationAutoDetector.get_current_view_models()
        for app_label, view_name in views:
            view = apps.get_model(app_label, view_name)
            if issubclass(view, DBMaterializedView):
                if not self._check_view_exists(view):
                    self.logger.warning(f"View {view._meta.label} does not exist")
                    continue
                self.logger.info(f"Refreshing view {view._meta.label}")
                view.refresh(using=settings.DATA_DB_ALIAS)
                self.logger.info(f"Refreshed view {view._meta.label}")

    def _ensure_readonly_users(self):
        # Implement logic to ensure readonly users have appropriate permissions
        user_models = {
            "alexa": [*DEFAULT_SHARED_MODELS],
            "chrisd": [*DEFAULT_SHARED_MODELS],
            "diarmuid": [*DEFAULT_SHARED_MODELS],
            "karl": [*DEFAULT_SHARED_MODELS],
            "kva": [*DEFAULT_SHARED_MODELS],
            "priscilla": [*DEFAULT_SHARED_MODELS],
            "rcvda": [*DEFAULT_SHARED_MODELS],
            "read_only_user": [*DEFAULT_SHARED_MODELS],
            "superhighways": [
                "ftc.superhighwaysareaofoperation",
                "ftc.superhighwaysclassification",
                "ftc.superhighwayslondonorganisations",
                "ftc.superhighwaystrustees",
                "ftc.superhighwayslondonorganisationsview",
            ],
            "threesixtygiving": [*DEFAULT_SHARED_MODELS],
        }

        with connections[settings.DATA_DB_ALIAS].cursor() as cursor:
            for username, models in user_models.items():
                """Check if user already exists"""
                if not self._check_user_exists(username, cursor):
                    self.logger.warning(f"User {username} does not exist")
                    continue

                user_model_list = []
                for model in models:
                    app, model_name = model.split(".")
                    if model_name == "*":
                        app_models = apps.get_app_config(app).get_models()
                        for app_model in app_models:
                            user_model_list.append((username, app_model))
                    else:
                        user_model_list.append(
                            (username, apps.get_model(app, model_name))
                        )

                for user, model in user_model_list:
                    # check if the table/view actually exists
                    if not self._check_view_exists(model, cursor):
                        self.logger.warning(
                            f"Table/view {model._meta.db_table} does not exist"
                        )
                        continue

                    self.logger.info(
                        f"Ensuring readonly permissions for user {user} on model {model._meta.label}"
                    )
                    cursor.execute(
                        sql.SQL("GRANT SELECT ON {} TO {}").format(
                            sql.Identifier(model._meta.db_table),
                            sql.Identifier(user),
                        )
                    )
