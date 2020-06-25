Find that charity
================

Elasticsearch-powered search engine for looking for charities. Allows for:

- importing data from England and Wales, Scotland, and Northern Ireland, ensuring that duplicates
  are matched to one record.
- An elasticsearch index that can be queried.
- [Org-ids](http://org-id.guide/about) are added to charities.
- Reconciliation API for searching charity, based on an optimised search query.
- Facility for uploading a CSV of charity names and adding the (best guess) at a
  charity number.
- HTML pages for searching for a charity

Installation
------------

1. [Clone repository](https://github.com/TechforgoodCAST/find-that-charity)
2. Create virtual environment (`python -m venv env`)
3. Activate virtual environment (`env/bin/activate` or `env/Scripts\activate`)
4. Install requirements (`pip install -r requirements.txt`)
5. [Install elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/_installation.html)
6. Start elasticsearch
7. Create elasticsearch index (`python data_import/create_elasticsearch.py`)

Dokku Installation
------------------

### 1. Set up dokku server

SSH into server and run:

```bash
# create app
dokku apps:create find-that-charity

# add permanent data storage
dokku storage:mount find-that-charity /var/lib/dokku/data/storage/find-that-charity:/data

# elasticsearch
sudo dokku plugin:install https://github.com/dokku/dokku-elasticsearch.git elasticsearch
export ELASTICSEARCH_IMAGE="elasticsearch"
export ELASTICSEARCH_IMAGE_VERSION="2.4"
dokku elasticsearch:create find-that-charity-es
dokku elasticsearch:link find-that-charity-es find-that-charity

# SSL
sudo dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
dokku config:set --no-restart find-that-charity DOKKU_LETSENCRYPT_EMAIL=your@email.tld
dokku letsencrypt find-that-charity
dokku letsencrypt:cron-job --add

# create app storage
mkdir -p /var/lib/dokku/data/storage/ftc-uploads
chown -R dokku:dokku /var/lib/dokku/data/storage/ftc-uploads
chown -R 32767:32767 /var/lib/dokku/data/storage/ftc-uploads
dokku storage:mount find-that-charity /var/lib/dokku/data/storage/ftc-uploads:/app/data
dokku config:set find-that-charity FOLDER=/app/data
```

### 2. Add as a git remote and push

On local machine:

```bash
git remote add dokku dokku@SERVER_HOST:find-that-charity
git push dokku master
```

### 3. Setup and run import

On Dokku server run:

```bash
# setup and run import
dokku run find-that-charity python data_import/create_elasticsearch.py
dokku run find-that-charity python data_import/fetch_data.py --folder '/data'
dokku run find-that-charity python data_import/import_data.py --folder '/data'
```

### 4. Set up scheduled task for running tasks on a regular basis

On dokku server add a cron file at `/etc/cron.d/find-that-charity`

```bash
nano /etc/cron.d/find-that-charity
```

Then paste in the file contents, and press `CTRL+X` then `Y` to save.

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

# fetch latest charity data from the regulators
# run at 2am on the 13th of the month
0 2 13 * * dokku dokku run find-that-charity python data_import/fetch_data.py --folder '/app/data'

# import latest charity data
# run at 4am on the 13th of the month
0 4 13 * * dokku dokku run find-that-charity python data_import/import_data.py --folder '/app/data'

### PLACE ALL CRON TASKS ABOVE, DO NOT REMOVE THE WHITESPACE AFTER THIS LINE
```

Fetching data
-------------

This step fetches data on charities in England, Wales and Scotland. The command
is run using the following command:

`python data_import/fetch_data.py --oscr <path/to/oscr/zip/file.zip>`

### Office of the Scottish Charity Regulator (OSCR)

OSCR data needs to be manually downloaded from the [OSCR website](https://www.oscr.org.uk/about-charities/search-the-register/charity-register-download)
in order to accept the terms and conditions. Once downloaded the path needs to
be passed to `data_import/fetch_data.py` using the `--oscr` flag.

### Charity Commission for England and Wales

Data on charities in England and Wales will be fetched from <http://data.charitycommission.gov.uk/>.
If a different URL is needed then use the `--ccew` flag.

The latest .ZIP file will be downloaded and unzipped, and the data contained
will be converted from `.bcp` files to `.csv`.

### Charity Commission for Northern Ireland

Data on charities in Northern Ireland will be fetched from <http://www.charitycommissionni.org.uk/charity-search/> (Open Government Licence)
If a different URL is needed then pass it to the `--ccni` flag when running `import/fetch_data.py`

The latest .CSV file (updated daily) will be downloaded to /data.

"Other names" for Northern Ireland charities are not contained in the downloadable CSV, but are in the information presented on the CCNI website. The other names are maintained [in this list](https://gist.github.com/BobHarper1/2687545c562b47bc755aef2e9e0de537) which will be downloaded. To use another file, pass url to `--ccni_extra`.

### Dual registered charities

A list of [dual registered charities](https://gist.github.com/drkane/22d62e07346084fafdcc7d9f5e1cd661/raw/bec666d1bc5c6efb8503a90f76ac0c6236ebc183/dual-registered-uk-charities.csv)
will be downloaded from github. To use another file pass an url to `--dual`.

The list is CSV file with a line per pair of England and Wales/Scottish charities
in the format:

```csv
"Scottish Charity Number","E&W Charity Number","Charity Name (E&W)"
"SC002327","263710","Shelter, National Campaign for Homeless People Limited"
```

To add more charities fork the to the [Github gist](https://gist.github.com/drkane/22d62e07346084fafdcc7d9f5e1cd661)
and add a comment to the original gist.

Postcode data
-------------

You can also add postcode data from <https://github.com/drkane/es-postcodes> to
allow for geographic-based searching. If you host the postcode elasticsearch
index on the same host it can be used at the `import_data.py` stage.

Importing data
--------------

Once the data has been fetched the needed files are stored `data/` directory.
You can then run the `python data_import/import_data.py` script to import it.

By default the script will look for an elasticsearch instance at <localhost:9200>,
use `python data_import/import_data.py --help` to see the available options. To use the
postcode elasticsearch index you need to pass `--es-pc-host localhost`.

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

The server uses [bottle](http://bottlepy.org/docs/dev/). Run it with the
following command:

`python server/server.py --host localhost --port 8080`

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
=======


# Setup steps

## Import organisations

```sh
python ./manage.py import_companies
python ./manage.py import_charities
python ./manage.py import_all
```

## Populate the elasticsearch index

run

https://github.com/dokku/dokku-elasticsearch/issues/72 - set up es 7.X

```sh
python ./manage.py search_index --rebuild --no-count

# or

python ./manage.py search_index --populate --no-count
```


