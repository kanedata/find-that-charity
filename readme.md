# Find that charity

Elasticsearch-powered search engine for looking for charities and other non-profit organisations. Allows for:

- importing data nearly 20 sources in the UK, ensuring that duplicates
  are matched to one record.
- An elasticsearch index that can be queried.
- [Org-ids](http://org-id.guide/about) are added to organisations.
- Reconciliation API for searching organisations, based on an optimised search query.
- Facility for uploading a CSV of charity names and adding the (best guess) at a
  charity number.
- HTML pages for searching for a charity

## Installation

1. [Clone repository](https://github.com/kanedata/find-that-charity)
2. Create virtual environment (`python -m venv env`)
3. Activate virtual environment (`env/bin/activate` or `env/Scripts\activate`)
4. Install requirements (`pip install -r requirements.txt`)
5. [Install postgres](https://www.postgresql.org/download/)
6. Start postgres
7. Create 2 postgres databases - one for admin (eg `ftc_admin` and one for data eg `ftc_data`)
8. [Install elasticsearch 7](https://www.elastic.co/guide/en/elasticsearch/reference/current/_installation.html) - you may need to increase available memory (see below)
9. Start elasticsearch
10. Create `.env` file in root directory. Contents based on `.env.example`.
11. Create the database tables (`python ./manage.py migrate --database=data && python ./manage.py migrate --database=admin && python ./manage.py createcachetable --database=admin`)
12. Import data on charities (`python ./manage.py import_charities`)
13. Import data on nonprofit companies (`python ./manage.py import_ch`)
14. Import data on other non-profit organisations (`python ./manage.py import_all`)
15. Add organisations to elasticsearch index (`python ./manage.py es_index`) - (Don't use the default `search_index` command as this won't setup aliases correctly)

## Dokku Installation

### 1. Set up dokku server

SSH into server and run:

```bash
# create app
dokku apps:create ftc

# postgres
sudo dokku plugin:install https://github.com/dokku/dokku-postgres.git postgres
dokku postgres:create ftc-db-data
dokku postgres:link ftc-db-data ftc --alias "DATABASE_URL"
dokku postgres:create ftc-db-admin
dokku postgres:link ftc-db-admin ftc --alias "DATABASE_ADMIN_URL"

# elasticsearch
sudo dokku plugin:install https://github.com/dokku/dokku-elasticsearch.git elasticsearch
echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf; sudo sysctl -p
export ELASTICSEARCH_IMAGE="elasticsearch"
export ELASTICSEARCH_IMAGE_VERSION="7.7.1"
dokku elasticsearch:create ftc-es
dokku elasticsearch:link ftc-es ftc
# configure elasticsearch 7:
# https://github.com/dokku/dokku-elasticsearch/issues/72#issuecomment-510771763

# setup elasticsearch increased memory (might be needed)
nano /var/lib/dokku/services/elasticsearch/ftc-es/config/jvm.options
# replace `-Xms512m` with `-Xms2g`
# replace `-Xms512m` with `-Xmx2g`
# restart elasticsearch
dokku elasticsearch:restart ftc-es

# Redirect
dokku plugin:install https://github.com/dokku/dokku-redirect.git
dokku redirect:set ftc www.findthatcharity.uk findthatcharity.uk

# SSL
sudo dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
dokku letsencrypt:set ftc email your@email.tld
dokku letsencrypt:enable ftc
dokku letsencrypt:cron-job --add
```

### 2. Add as a git remote and push

On local machine:

```bash
git remote add dokku dokku@SERVER_HOST:ftc
git push dokku main
```

### 3. Setup and run import

On Dokku server run:

```bash
# setup
dokku run ftc python ./manage.py migrate --database=data
dokku run ftc python ./manage.py migrate --database=admin
dokku run ftc python ./manage.py createcachetable --database=admin

# run import
dokku run ftc python ./manage.py charity_setup
dokku run ftc python ./manage.py import_oscr
dokku run ftc python ./manage.py import_charities
dokku run ftc python ./manage.py import_ch
dokku run ftc python ./manage.py import_other_data
dokku run ftc python ./manage.py import_all
dokku run ftc python ./manage.py es_index
```

## Server

The server uses [django](https://www.djangoproject.com/). Run it with the
following command:

`python ./manage.py runserver`

The server offers the following API endpoints:

- `/reconcile`: a [reconciliation service API](https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation-Service-API)
  conforming to the OpenRefine reconciliation API specification.

- `/charity/12345`: Look up information about a particular charity

## Todo

Priorities:

- tests for ensuring data is correctly imported
- server tests
- use results of `server/recon_test.py` to produce the best reconciliation
  search query for use in the server (`recon_test_7` seems the best at the moment)
- threshold for when to use the result vs discard

Future development:

- upload a CSV file and reconcile each row with a charity
- allow updating a charity with additional possible names

## Testing

```sh
coverage run pytest && coverage html
python -m http.server -d htmlcov --bind 127.0.0.1 8001
```
