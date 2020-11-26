Find that charity
================

Elasticsearch-powered search engine for looking for charities and other non-profit organisations. Allows for:

- importing data nearly 20 sources in the UK, ensuring that duplicates
  are matched to one record.
- An elasticsearch index that can be queried.
- [Org-ids](http://org-id.guide/about) are added to organisations.
- Reconciliation API for searching organisations, based on an optimised search query.
- Facility for uploading a CSV of charity names and adding the (best guess) at a
  charity number.
- HTML pages for searching for a charity

Installation
------------

1. [Clone repository](https://github.com/drkane/find-that-charity)
2. Create virtual environment (`python -m venv env`)
3. Activate virtual environment (`env/bin/activate` or `env/Scripts\activate`)
4. Install requirements (`pip install -r requirements.txt`)
5. [Install postgres](https://www.postgresql.org/download/)
6. Start postgres
7. [Install elasticsearch 7](https://www.elastic.co/guide/en/elasticsearch/reference/current/_installation.html) - you may need to increase available memory (see below)
8. Start elasticsearch
9. Create `.env` file in root directory. Contents based on `.env.example`.
10. Create the database tables (`python ./manage.py migrate && python ./manage.py createcachetable`)
11. Import data on charities (`python ./manage.py import_charities`)
12. Import data on nonprofit companies (`python ./manage.py import_companies`)
13. Import data on other non-profit organisations (`python ./manage.py import_all`)
14. Add organisations to elasticsearch index (`python ./manage.py es_index`) - (Don't use the default `search_index` command as this won't setup aliases correctly)

Dokku Installation
------------------

### 1. Set up dokku server

SSH into server and run:

```bash
# create app
dokku apps:create ftc

# postgres
sudo dokku plugin:install https://github.com/dokku/dokku-postgres.git postgres
dokku postgres:create ftc-db
dokku postgres:link ftc-db ftc

# elasticsearch
sudo dokku plugin:install https://github.com/dokku/dokku-elasticsearch.git elasticsearch
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

# SSL
sudo dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
dokku config:set --no-restart ftc DOKKU_LETSENCRYPT_EMAIL=your@email.tld
dokku letsencrypt ftc
dokku letsencrypt:cron-job --add
```

### 2. Add as a git remote and push

On local machine:

```bash
git remote add dokku dokku@SERVER_HOST:ftc
git push dokku master
```

### 3. Setup and run import

On Dokku server run:

```bash
# setup and run import
dokku run ftc python ./manage.py charity_setup
dokku run ftc python ./manage.py import_charities
dokku run ftc python ./manage.py import_companies
dokku run ftc python ./manage.py import_all
dokku run ftc python ./manage.py es_index
```

### 4. Set up scheduled task for running tasks on a regular basis

On dokku server add a cron file at `/etc/cron.d/ftc`

```bash
nano /etc/cron.d/ftc
```

Then paste in the [file contents](crontab), and press `CTRL+X` then `Y` to save.

File contents:

```bash
# server cron jobs
MAILTO="mail@example.com"
PATH=/usr/local/bin:/usr/bin:/bin
SHELL=/bin/bash

# m   h   dom mon dow   username command
# *   *   *   *   *     dokku    command to be executed
# -   -   -   -   -
# |   |   |   |   |
# |   |   |   |   +----- day of week (0 - 6) (Sunday=0)
# |   |   |   +------- month (1 - 12)
# |   |   +--------- day of month (1 - 31)
# |   +----------- hour (0 - 23)
# +----------- min (0 - 59)

### KEEP SORTED IN TIME ORDER

### PLACE ALL CRON TASKS BELOW

# import everything else - every night
0 1 * * * dokku dokku --rm run ftc python ./manage.py import_all

# import charities - Thursday night
# import_oscr is run first because it seems to time out in the middle of the night
0 20 * * 4 dokku dokku --rm run ftc python ./manage.py import_oscr
0 2 * * 5 dokku dokku --rm run ftc python ./manage.py import_charities

# import companies - Friday night
0 2 * * 6 dokku dokku --rm run ftc python ./manage.py import_companies

# regenerate the elasticsearch index - every night
0 4 * * * dokku dokku --rm run ftc python ./manage.py es_index

### PLACE ALL CRON TASKS ABOVE, DO NOT REMOVE THE WHITESPACE AFTER THIS LINE
```

Fetching data
-------------

This step fetches data on charities in England, Wales and Scotland. The command
is run using the following command:

```sh
python ./manage.py import_charities
```

### Data model

The data is imported into elasticsearch in the following format:

```json
{
  "charity_number": "12355",
  "ccew_number": "12355",
  "oscr_number": "SC1235",
  "ccni_number": "NIC100012",
  "active": true,
  "names": [
    {"name": "Charity Name", "type": "registered name", "source": "ccew"}
  ],
  "known_as": "Charity Name",
  "geo": {
    "areas": ["gss_codes"],
    "postcode": "PO54 0DE",
    "latlng": [0.0, 50.0]
  },
  "url": "http://www.url.org.uk/",
  "domain": "url.org.uk",
  "latest_income": 12345,
  "company_number": [
    {"number": "00121212", "source": "ccew"}
  ],
  "parent": "124566",
  "ccew_link": "http://apps.charitycommission.gov.uk/Showcharity/RegisterOfCharities/SearchResultHandler.aspx?RegisteredCharityNumber=12355&SubsidiaryNumber=0",
  "oscr_link": "https://www.oscr.org.uk/about-charities/search-the-register/charity-details?number=SC1235",
  "ccni_link": "http://www.charitycommissionni.org.uk/charity-details/?regid=100012&subid=0",
  "org-ids": ["GB-COH-00121212", "GB-CHC-12355", "GB-SC-SC1235", "GB-NIC-100012"],
  "date_registered": "2001-01-01T00:00:00",
  "date_removed": null,
  "last_modified": "2018-02-11T22:49:15"
}
```

Server
------

The server uses [django](https://www.djangoproject.com/). Run it with the
following command:

`python ./manage.py runserver`

The server offers the following API endpoints:

- `/reconcile`: a [reconciliation service API](https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation-Service-API)
  conforming to the OpenRefine reconciliation API specification.

- `/charity/12345`: Look up information about a particular charity

Todo
----

Current status is a proof-of-concept, needs a bit of work to get up and running.

Priorities:

- tests for ensuring data is correctly imported
- server tests
- use results of `server/recon_test.py` to produce the best reconciliation
  search query for use in the server (`recon_test_7` seems the best at the moment)
- threshold for when to use the result vs discard

Future development:

- upload a CSV file and reconcile each row with a charity
- allow updating a charity with additional possible names
