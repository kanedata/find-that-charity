from django.conf import settings
from django.db import models


class OrganisationTag(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name="tagged_organisations",
    )
    org_id = models.CharField(max_length=100)
    tag = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "org_id", "tag")

    def __str__(self):
        return f"{self.user} tagged {self.org_id} with {self.tag}"


class DatabaseUser(models.Model):
    usename = models.CharField(
        max_length=100, help_text="Name of this user", verbose_name="Username"
    )
    usesysid = models.IntegerField(
        primary_key=True, help_text="ID of this user", verbose_name="User ID"
    )
    usecreatedb = models.BooleanField(
        help_text="User can create databases", verbose_name="Can create databases"
    )
    usesuper = models.BooleanField(
        help_text="User is a superuser", verbose_name="Superuser"
    )
    userepl = models.BooleanField(
        help_text="User can initiate streaming replication and put the system in and out of backup mode.",
        verbose_name="Can initiate replication",
    )
    usebypassrls = models.BooleanField(
        help_text="User bypasses every row-level security policy",
        verbose_name="Bypass row-level security",
    )
    passwd = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Not the password (always reads as ********)",
        verbose_name="Password",
    )
    valuntil = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Password expiry time (only used for password authentication)",
        verbose_name="Password expiry time",
    )
    useconfig = models.TextField(
        blank=True,
        null=True,
        help_text="Session defaults for run-time configuration variables",
        verbose_name="Session defaults",
    )

    class Meta:
        ordering = ("usename",)
        managed = False
        db_table = "pg_user"

    def __str__(self):
        return self.usename

    def is_django_db_user(self, connection):
        return self.usename == connection.get_connection_params()["user"]
