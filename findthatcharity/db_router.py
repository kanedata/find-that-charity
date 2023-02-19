class DBRouter:
    """
    A router to decide whether the data or admin database should be used.
    """

    route_app_labels = {
        "addtocsv",
        "api",
        "charity",
        "companies",
        "charity_django.companies",
        "ftcbot",
        "ftc",
        "geo",
        "other_data",
        "reconcile",
    }
    admin_db = "admin"
    data_db = "data"

    def db_for_read(self, model, **hints):
        """
        Attempts to read data types go to data_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return self.data_db
        return self.admin_db

    def db_for_write(self, model, **hints):
        """
        Attempts to write data types go to data_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return self.data_db
        return self.admin_db

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
        if app_label in self.route_app_labels:
            return db == self.data_db
        return db == self.admin_db
