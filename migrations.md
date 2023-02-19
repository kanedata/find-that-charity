# Migration to new version with API

## Split the database

- manually create new database
- move admin tables over to new admin DB
- set DATABASE_ADMIN_URL to address of new DB

## Changes to companies database tables

- change existing companies tables
- remove existing companies migrations (`DELETE FROM django_migrations WHERE app = 'companies'`) on both databases
- rename companies tables
- run the compmanies migrations
- move data from old tables to new ones
- delete old tables