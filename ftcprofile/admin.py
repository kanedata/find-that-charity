from django import forms
from django.contrib import admin, messages
from django.db import ProgrammingError, connections
from django.template.loader import render_to_string
from django.utils.html import format_html_join, mark_safe
from psycopg2 import sql

from findthatcharity.db_router import DBRouter
from ftcprofile.models import DatabaseUser

CREATE_USER_SQL = [
    "CREATE ROLE {usename} WITH LOGIN PASSWORD %(password)s NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION VALID UNTIL 'infinity'",
    "GRANT CONNECT ON DATABASE {dbname} TO {usename}",
    "GRANT USAGE ON SCHEMA public TO {usename}",
    "GRANT SELECT ON ALL TABLES IN SCHEMA public TO {usename}",
    "GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO {usename}",
    "REVOKE SELECT ON django_migrations FROM {usename}",
]


def get_connection(obj):
    using_db = DBRouter().db_for_write(obj)
    return connections[using_db]


def execute_sql(sql_queries, params, obj):
    connection = get_connection(obj)

    identifier_params = {
        k: sql.Identifier(v)
        for k, v in {
            **connection.get_connection_params(),
            **params,
        }.items()
        if isinstance(v, str)
    }

    results = []
    with connection.cursor() as cursor:
        for sql_query in sql_queries:
            sql_query = sql.SQL(sql_query).format(**identifier_params)
            cursor.execute(sql_query, params)
            try:
                results.append(cursor.fetchall())
            except ProgrammingError:
                continue
    return results


class DatabaseUserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = DatabaseUser
        fields = ("usename",)

    def save(self, commit=True):
        execute_sql(CREATE_USER_SQL, self.cleaned_data, DatabaseUser)
        user = DatabaseUser.objects.get(usename=self.cleaned_data["usename"])
        return user

    def save_m2m(self):
        pass


@admin.register(DatabaseUser)
class DatabaseUserAdmin(admin.ModelAdmin):
    list_display = (
        "usesysid",
        "usename",
        "usecreatedb",
        "usesuper",
        "database",
        "privileges",
        "is_django_db_user",
    )
    list_filter = ("usecreatedb", "usesuper")
    search_fields = ("usename",)
    ordering = ("usename",)
    list_display_links = ("usename",)
    readonly_fields = ("is_django_db_user", "database", "privileges", "tables")

    def add_view(self, request, extra_content=None):
        self._original_form = self.form
        self.form = DatabaseUserCreateForm
        return super(DatabaseUserAdmin, self).add_view(request)

    def change_view(self, request, object_id, extra_content=None):
        if hasattr(self, "_original_form"):
            self.form = self._original_form
        return super(DatabaseUserAdmin, self).change_view(request, object_id)

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        if obj:
            return not obj.usesuper
        return True

    def database(self, obj):
        return DBRouter().db_for_write(obj)

    def privileges(self, obj):
        result = execute_sql(
            [
                """
                SELECT privilege_type,
                    COUNT(distinct (table_schema::text || table_name::text)) as num_tables
                FROM information_schema.table_privileges
                WHERE grantee = %(usename)s
                group by 1
                """
            ],
            {"usename": obj.usename},
            obj,
        )
        return format_html_join("\n", "<li>{} ({} tables)", result[0])

    def tables(self, obj):
        result = execute_sql(
            [
                """
                SELECT table_schema, table_name, privilege_type
                FROM information_schema.table_privileges
                WHERE grantee = %(usename)s
                """
            ],
            {"usename": obj.usename},
            obj,
        )
        tables = {}
        privileges = {
            "SELECT",
            "DELETE",
            "INSERT",
            "UPDATE",
            "TRUNCATE",
            "REFERENCES",
            "TRIGGER",
        }
        for table_schema, table_name, privilege_type in result[0]:
            tables.setdefault(
                (
                    table_schema,
                    table_name,
                ),
                [],
            ).append(privilege_type)
            privileges.add(privilege_type)
        tables = dict(sorted(tables.items()))
        public_tables = {k: v for k, v in tables.items() if k[0] == "public"}
        other_tables = {k: v for k, v in tables.items() if k[0] != "public"}
        table_html = render_to_string(
            "admin/db_user_table.html.j2",
            context={
                "public_tables": public_tables,
                "other_tables": other_tables,
                "privileges": sorted(privileges),
            },
        )
        return mark_safe(table_html)

    @admin.display(boolean=True)
    def is_django_db_user(self, obj):
        connection = get_connection(obj)
        return obj.is_django_db_user(connection)

    def save_model(self, request, obj, form, change):
        pass

    def delete_model(self, request, obj):
        delete_sql = [
            "REASSIGN OWNED BY {usename} TO {user}",
            "REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM {usename}",
            "REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM {usename}",
            "REVOKE ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public FROM {usename}",
            "REVOKE CONNECT ON DATABASE {dbname} FROM {usename}",
            "REVOKE ALL ON SCHEMA public FROM {usename}",
            "DROP ROLE {usename}",
        ]
        connection = get_connection(obj)

        if obj.usename == connection.get_connection_params()["user"]:
            messages.error(request, "You cannot delete the default user.")
            return

        execute_sql(delete_sql, {"usename": obj.usename}, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.delete_model(request, obj)
