"""
Run the find that charity server
"""
from __future__ import print_function
import os
import argparse
import json
from collections import OrderedDict
import time
from datetime import datetime, timezone
import re

from dateutil import parser
import bottle
from elasticsearch import Elasticsearch
import requests
from bs4 import BeautifulSoup

from queries import search_query, recon_query, service_spec, esdoc_orresponse
from csv_upload import csv_app

app = bottle.default_app()
app.merge(csv_app)

# everywhere gives a different env var for elasticsearch services...
POTENTIAL_ENV_VARS = [
    "ELASTICSEARCH_URL",
    "ES_URL",
    "BONSAI_URL"
]
for e_v in POTENTIAL_ENV_VARS:
    if os.environ.get(e_v):
        app.config["es"] = Elasticsearch(os.environ.get(e_v))
        app.config["es_index"] = 'charitysearch'
        app.config["es_type"] = 'charity'
        break

if os.environ.get("GA_TRACKING_ID"):
    app.config["ga_tracking_id"] = os.environ.get("GA_TRACKING_ID")

if os.environ.get("ADMIN_PASSWORD"):
    app.config["admin_password"] = os.environ.get("ADMIN_PASSWORD")

csv_app.config.update(app.config)


def search_return(query):
    """
    Fetch search results and display on a template
    """
    res = app.config["es"].search_template(
        index=app.config["es_index"],
        doc_type=app.config["es_type"],
        body=query,
        ignore=[404]
    )
    res = res["hits"]
    for result in res["hits"]:
        result["_link"] = "/charity/" + result["_id"]
        result["_source"] = sort_out_date(result["_source"])
    return bottle.template('search', res=res, term=json.loads(query)["params"]["name"])


@app.route('/')
def home():
    """
    Get the index page for the site
    """
    query = bottle.request.query.get('q')
    if query:
        query = search_query(query)
        return search_return(query)
    return bottle.template('index', term='')


@app.route('/random')
@app.route('/random.<filetype>')
def random(filetype="html"):
    """ Get a random charity record
    """
    query = {
        "size": 1,
        "query": {
            "function_score": {
                "functions": [
                    {
                        "random_score": {
                            "seed": str(time.time())
                        }
                    }
                ]
            }
        }
    }

    if "active" in bottle.request.query:
        query["query"]["function_score"]["query"] = {"match": {"active": True}}

    res = app.config["es"].search(
        index=app.config["es_index"],
        doc_type=app.config["es_type"],
        body=query,
        ignore=[404]
    )
    char = None
    if "hits" in res:
        if "hits" in res["hits"]:
            char = res["hits"]["hits"][0]

    if char:
        if filetype == "html":
            bottle.redirect("/charity/{}".format(char["_id"]))
        return char["_source"]



@app.route('/reconcile')
@app.post('/reconcile')
def reconcile():
    """ Index of the server. If ?query or ?queries used then search,
                otherwise return the default response as JSON
    """
    query = recon_query(bottle.request.query.query) or None
    queries = bottle.request.params.queries or None

    service_url = "{}://{}".format(
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc,
    )

    # if we're doing a callback request then do that
    if bottle.request.query.callback:
        if bottle.request.query.query:
            bottle.response.content_type = "application/javascript"
            return "%s(%s)" % (bottle.request.query.callback, esdoc_orresponse(query, app))
        else:
            return "%s(%s)" % (bottle.request.query.callback, service_spec(app, service_url))

    # try fetching the query as json data or a string
    if bottle.request.query.query:
        return esdoc_orresponse(query, app)

    if queries:
        queries_json = json.loads(queries)
        queries_dict = json.loads(queries, object_pairs_hook=OrderedDict)
        results = {}
        counter = 0
        for query_id in queries_dict:
            result = esdoc_orresponse(recon_query(
                queries_json[query_id]["query"]), app)["result"]
            results.update({query_id: {"result": result}})
            counter += 1
        return results

    # otherwise just return the service specification
    return service_spec(app, service_url)


@app.route('/charity/<regno>')
@app.route('/charity/<regno>.<filetype>')
def charity(regno, filetype='html'):
    """
    Return a single charity record
    """

    regno_cleaned = clean_regno(regno)
    if regno_cleaned == "":
        return bottle.abort(404, bottle.template(
            'Charity {{regno}} not found.', regno=regno))

    res = app.config["es"].get(index=app.config["es_index"],
                               doc_type=app.config["es_type"], id=regno_cleaned, ignore=[404])
    if "_source" in res:
        if filetype == "html":
            return bottle.template('charity', charity=sort_out_date(res["_source"]), charity_id=res["_id"])
        return res["_source"]
    else:
        return bottle.abort(404, bottle.template('Charity {{regno}} not found.', regno=regno))


@app.route('/preview/charity/<regno>')
@app.route('/preview/charity/<regno>.html')
def charity_preview(regno):
    """
    Small version of charity record

    Used in reconciliation API
    """
    res = app.config["es"].get(index=app.config["es_index"], doc_type=app.config["es_type"], id=regno, ignore=[404])
    if "_source" in res:
        return bottle.template('preview', charity=sort_out_date(res["_source"]), charity_id=res["_id"], hide_title=("hide_title" in bottle.request.params))
    bottle.abort(404, bottle.template('Charity {{regno}} not found.', regno=regno))


@app.route('/orgid/<orgid>.json')
def orgid_json(orgid):
    """
    Fetch json representation based on a org-id for a record
    """
    query = {
        "query": {
            "match": {
                "org-ids": {
                    "query": orgid,
                    "operator": "and",
                }
            }
        }
    }
    res = app.config["es"].search(index=app.config["es_index"],
                                  doc_type=app.config["es_type"],
                                  body=query,
                                  _source_exclude=["complete_names"],
                                  ignore=[404])
    if res.get("hits", {}).get("hits", []):
        org = res["hits"]["hits"][0]["_source"]
        org.update({"id": res["hits"]["hits"][0]["_id"]})
        return org
    bottle.abort(404, bottle.template(
        'Orgid {{orgid}} not found.', orgid=orgid))

@app.route('/orgid/<orgid>')
@app.route('/orgid/<orgid>.html')
def orgid_html(orgid):
    """
    Redirect to a record based on the org-id
    """
    org = orgid_json(orgid)
    bottle.redirect('/charity/{}'.format(org["id"]))


@app.route('/feeds/ccew.<filetype>')
def ccew_rss(filetype):
    """
    Get an RSS feed based on when data is
    uploaded by the Charity Commission
    """
    ccew_url = 'http://data.charitycommission.gov.uk/'
    res = requests.get(ccew_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    items = []
    for i in soup.find_all('blockquote'):
        links = i.find_all('a')
        idate = parser.parse(
            i.h4.string.split(", ")[1],
            default=datetime(2018, 1, 12, 0, 0)
        ).replace(tzinfo=timezone.utc)
        items.append({
            "name": i.h4.string,
            "date": idate,
            "link": links[0].get('href'),
            "author": "Charity Commission for England and Wales",
        })

    feed_contents = dict(
        items=items,
        title='Charity Commission for England and Wales data downloads',
        description='Downloads available from Charity Commission data downloads page.',
        url=ccew_url,
        feed_url=bottle.request.url,
        updated=datetime.now().replace(tzinfo=timezone.utc),
    )

    if filetype == 'atom':
        bottle.response.content_type = 'application/atom+xml'
        template = 'atom.xml'
    elif filetype == "json":
        bottle.response.content_type = 'application/json'
        return {
            "version": "https://jsonfeed.org/version/1",
            "title": feed_contents["title"],
            "home_page_url": feed_contents["url"],
            "feed_url": feed_contents["feed_url"],
            "description": feed_contents["description"],
            "items": [
                {
                    "id": item["link"],
                    "url": item["link"],
                    "title": item["name"],
                    "date_published": item["date"].isoformat(),
                } for item in items
            ]
        }
    else:
        bottle.response.content_type = 'application/rss+xml'
        template = 'rss.xml'

    return bottle.template(template, **feed_contents)


@app.route('/about')
def about():
    """About page
    """
    return bottle.template('about', this_year=datetime.now().year)


@app.route('/autocomplete')
def autocomplete():
    """
    Endpoint for autocomplete queries
    """
    search = bottle.request.params.q
    doc = {
        "suggest": {
            "suggest-1": {
                "prefix": search,
                "completion": {
                    "field": "complete_names",
                    "fuzzy" : {
                        "fuzziness" : 1
                    }
                }
            }
        }
    }
    res = app.config["es"].search(
        index=app.config["es_index"], doc_type="csv_data", body=doc,
        _source_include=['known_as'])
    return {"results": [
        {
            "label": x["_source"]["known_as"],
            "value": x["_id"]
        } for x in res.get("suggest", {}).get("suggest-1", [])[0]["options"]
    ]}


@app.route('/static/<filename:path>')
def send_static(filename):
    """ Fetch static files
    """
    return bottle.static_file(filename, root='static')


def sort_out_date(charity_record):
    """
    parse date fields in a charity record
    """
    date_fields = ["date_registered", "date_removed", "last_modified"]
    for date_field in date_fields:
        if charity_record.get(date_field):
            try:
                charity_record[date_field] = parser.parse(
                    charity_record[date_field])
            except ValueError:
                pass
    return charity_record

def clean_regno(regno):
    """
    Clean up a charity registration number
    """
    regno = str(regno)
    regno = regno.upper()
    regno = re.sub(r'^[^0-9SCNI]+|[^0-9]+$', '', regno)
    return regno


def main():
    """
    Run the server (command line version)
    """

    parser_args = argparse.ArgumentParser(description='')  # @TODO fill in

    # server options
    parser_args.add_argument('-host', '--host', default="localhost", help='host for the server')
    parser_args.add_argument('-p', '--port', default=8080, help='port for the server')
    parser_args.add_argument('--debug', action='store_true', dest="debug", help='Debug mode (autoreloads the server)')
    parser_args.add_argument('--server', default="auto", help='Server backend to use (see http://bottlepy.org/docs/dev/deployment.html#switching-the-server-backend)')

    # http auth
    parser_args.add_argument('--admin-password', help='Password for accessing admin pages')

    # elasticsearch options
    parser_args.add_argument('--es-host', default="localhost", help='host for the elasticsearch instance')
    parser_args.add_argument('--es-port', default=9200, help='port for the elasticsearch instance')
    parser_args.add_argument('--es-url-prefix', default='', help='Elasticsearch url prefix')
    parser_args.add_argument('--es-use-ssl', action='store_true', help='Use ssl to connect to elasticsearch')
    parser_args.add_argument('--es-index', default='charitysearch', help='index used to store charity data')
    parser_args.add_argument('--es-type', default='charity', help='type used to store charity data')

    parser_args.add_argument('--ga-tracking-id', help='Google Analytics Tracking ID')

    args = parser_args.parse_args()

    app.config["es"] = Elasticsearch(
        host=args.es_host,
        port=args.es_port,
        url_prefix=args.es_url_prefix,
        use_ssl=args.es_use_ssl
    )
    app.config["es_index"] = args.es_index
    app.config["es_type"] = args.es_type
    app.config["ga_tracking_id"] = args.ga_tracking_id
    app.config["admin_password"] = args.admin_password

    csv_app.config.update(app.config)
    bottle.debug(args.debug)

    if not app.config["es"].ping():
        raise ValueError("Elasticsearch connection failed")

    bottle.run(app, server=args.server, host=args.host, port=args.port, reloader=args.debug)

if __name__ == '__main__':
    main()
