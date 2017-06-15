Find that charity
=================

Elasticsearch-powered search engine for looking for charities. Allows for:

- importing data from England and Wales, Scotland, and Northern Ireland, ensuring that duplicates
  are matched to one record.
- An elasticsearch index that can be queried.
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
7. Create elasticsearch index (`python import/create_elasticsearch.py`)

Fetching data
-------------

This step fetches data on charities in England, Wales and Scotland. The command
is run using the following command:

`python import/fetch_data.py --oscr <path/to/oscr/zip/file.zip>`

### Office of the Scottish Charity Regulator (OSCR)

OSCR data needs to be manually downloaded from the [OSCR website](http://www.oscr.org.uk/charities/search-scottish-charity-register/charity-register-download)
in order to accept the terms and conditions. Once downloaded the path needs to
be passed to `import/fetch_data.py` using the `--oscr` flag.

### Charity Commission for England and Wales

Data on charities in England and Wales will be fetched from <http://data.charitycommission.gov.uk/>.
If a different URL is needed then use the `--ccew` flag.

The latest .ZIP file will be downloaded and unzipped, and the data contained
will be converted from `.bcp` files to `.csv`.

### Charity Commission for Northern Ireland

Data on charities in Northern Ireland will be fetched from <http://www.charitycommissionni.org.uk/charity-search/> (Open Government Licence)
If a different URL is needed then pass it to the `--ccni` flag when running `import/fetch_data.py`

The latest .CSV file (updated daily) will be downloaded to /data.

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
You can then run the `python import/import_data.py` script to import it.

By default the script will look for an elasticsearch instance at <localhost:9200>,
use `python import/import_data.py --help` to see the available options. To use the
postcode elasticsearch index you need to pass `--es-pc-host localhost`.

### Data model

The data is imported into elasticsearch in the following format:

```json
{
  "charity_number": "12355",
  "ccew_number": "12355",
  "oscr_number": "SC1235",
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
  "parent": "124566"
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
