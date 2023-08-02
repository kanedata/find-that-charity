from django.conf import settings


class DBRouter:
    """
    A router to decide whether the data or admin database should be used.
    """

    route_app_labels = {
        "addtocsv": settings.DATA_DB_ALIAS,
        "api": settings.DATA_DB_ALIAS,
        "charity": settings.DATA_DB_ALIAS,
        "companies": settings.DATA_DB_ALIAS,
        "charity_django.companies": settings.DATA_DB_ALIAS,
        "ftcbot": settings.DATA_DB_ALIAS,
        "ftc": settings.DATA_DB_ALIAS,
        "geo": settings.DATA_DB_ALIAS,
        "other_data": settings.DATA_DB_ALIAS,
        "reconcile": settings.DATA_DB_ALIAS,
    }
    route_model_labels = {
        "ftcprofile.DatabaseUser": settings.DATA_DB_ALIAS,
    }
    admin_db = settings.ADMIN_DB_ALIAS
    data_db = settings.DATA_DB_ALIAS

    def _get_db(self, app_label, model_name, **kwargs):
        db = self.route_app_labels.get(
            app_label,
            self.route_model_labels.get(model_name, self.admin_db),
        )
        if db in (self.data_db, self.admin_db):
            return db

        return self.admin_db

    def db_for_read(self, model, **hints):
        """
        Attempts to read data types go to data_db.
        """
        return self._get_db(model._meta.app_label, model._meta.label, **hints)

    def db_for_write(self, model, **hints):
        """
        Attempts to write data types go to data_db.
        """
        return self._get_db(model._meta.app_label, model._meta.label, **hints)

    def allow_relation(self, obj1, obj2, **hints):
        """
        Only allow relations in the same database
        """
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth and contenttypes apps only appear in the
        'auth_db' database.
        """
        return db == self._get_db(app_label, model_name, **hints)
