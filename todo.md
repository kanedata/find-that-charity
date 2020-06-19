# Find that Charity v4 - tasks todo

## Organisation JSON response

- ✔ add JSON response

## Autocomplete API

- ✔ (but implemented with /reconcile/suggest?)
- ✔ Add vuejs app to front page
- allow to be filtered by orgtype
- better suggestions

## CSV data tool

- Use `/reconcile/?extend=...` and `/reconcile/propose_properties` to get data
- Design app in Vue JS
- org_id hashes like postcode app

## Setup

- document the steps needed to setup
    - create DB
    - setup cache tables
    - populate DB (import_all)
    - create and populate elasticsearch (`python findthatcharity/manage.py search_index --populate --no-count --parallel`)
    - something on static urls?
- set up ongoing tasks
    - populate DB
    - repopulate elasticsearch

## Companies data import

- ✔ needs coverting to new format

## Return a random organisation

- ✔ use elasticsearch query

## Front page search

- ✔ switch to elasticsearch
- ✔ add organisationTypePrimary to elasticsearch

## Set up data feeds

- charity commission data files - when are they updated

## Better charity pages

- financial overview
- filter charities
- get area profile

## Build and document rest API

- use django-rest-api?

## Build and document graphQL API

- probably a plugin for that?
