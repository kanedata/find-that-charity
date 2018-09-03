from __future__ import print_function
import os
import argparse
import json
import yaml
from collections import OrderedDict
import time
from datetime import datetime, timezone
from dateutil import parser

import bottle
from elasticsearch import Elasticsearch
import requests
from bs4 import BeautifulSoup

app = bottle.default_app()

# everywhere gives a different env var for elasticsearch services...
potential_env_vars = [
    "ELASTICSEARCH_URL",
    "ES_URL",
    "BONSAI_URL"
]
for e_v in potential_env_vars:
    if os.environ.get(e_v):
        app.config["es"] = Elasticsearch(os.environ.get(e_v))
        app.config["es_index"] = 'charitysearch'
        app.config["es_type"] = 'charity'
        break

if os.environ.get("GA_TRACKING_ID"):
    app.config["ga_tracking_id"] = os.environ.get("GA_TRACKING_ID")

def search_query(term):
    with open('./es_config.yml', 'rb') as yaml_file:
        json_q = yaml.load(yaml_file)
        for p in json_q["params"]:
            json_q["params"][p] = term
        return json.dumps(json_q)


def recon_query(term):
    with open('./recon_config.yml', 'rb') as yaml_file:
        json_q = yaml.load(yaml_file)
        for p in json_q["params"]:
            json_q["params"][p] = term
        return json.dumps(json_q)


def esdoc_orresponse(query):
    """Decorate the elasticsearch document to the OpenRefine response API

    Specification found here: https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation-Service-API#service-metadata
    """
    res = app.config["es"].search_template(
        index=app.config["es_index"],
        doc_type=app.config["es_type"],
        body=query,
        ignore=[404]
    )
    res["hits"]["result"] = res["hits"].pop("hits")
    for i in res["hits"]["result"]:
        i["id"] = i.pop("_id")
        i["type"] = [i.pop("_type")]
        i["score"] = i.pop("_score")
        i["index"] = i.pop("_index")
        i["source"] = i.pop("_source")
        i["name"] = i["source"]["known_as"] + " (" + i["id"] + ")"
        if not i["source"]["active"]:
            i["name"] += " [INACTIVE]"
        if i["name"].lower() == json.loads(query)["params"]["name"].lower() and i["score"] == res["hits"]["max_score"]:
            i["match"] = True
        else:
            i["match"] = False
    return res["hits"]


def service_spec():
    """Return the default service specification

    Specification found here: https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation-Service-API#service-metadata
    """
    service_url = "{}://{}".format(
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc,
    )
    return {
        "name": app.config["es_index"],
        "identifierSpace": "http://rdf.freebase.com/ns/type.object.id",
        "schemaSpace": "http://rdf.freebase.com/ns/type.object.id",
        "view": {
            "url": service_url + "/charity/{{id}}"
        },
        "preview": {
            "url": service_url + "/preview/charity/{{id}}",
            "width": 430,
            "height": 300
        },
        "defaultTypes": [{
            "id": "/" + app.config["es_type"],
            "name": app.config["es_type"]
        }]
    }


def search_return(query):
    res = app.config["es"].search_template(index=app.config["es_index"], doc_type=app.config["es_type"], body=query, ignore=[404])
    res = res["hits"]
    for result in res["hits"]:
        result["_link"] = "/charity/" + result["_id"]
        result["_source"] = sort_out_date(result["_source"])
    return bottle.template('search', res=res, term=json.loads(query)["params"]["name"])


@app.route('/')
def home():
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
        if filetype=="html":
            bottle.redirect("/charity/{}".format(char["_id"]))
        else:
            return char["_source"]



@app.route('/reconcile')
@app.post('/reconcile')
def reconcile():
    """ Index of the server. If ?query or ?queries used then search,
                otherwise return the default response as JSON
    """
    query = recon_query(bottle.request.query.query) or None
    queries = bottle.request.params.queries or None

    # if we're doing a callback request then do that
    if bottle.request.query.callback:
        if bottle.request.query.query:
            bottle.response.content_type = "application/javascript"
            return "%s(%s)" % (bottle.request.query.callback, esdoc_orresponse(query))
        else:
            return "%s(%s)" % (bottle.request.query.callback, service_spec())

    # try fetching the query as json data or a string
    if bottle.request.query.query:
        return esdoc_orresponse(query)

    if queries:
        queries_json = json.loads(queries)
        queries_dict = json.loads(queries, object_pairs_hook=OrderedDict)
        # print(queries)
        results = {}
        counter = 0
        for query in queries_dict:
            q = "q" + str(counter)
            # print(queries_json[q], queries_json[q]["query"])
            result = esdoc_orresponse(recon_query(queries_json[q]["query"]))["result"]
            results.update({q: {"result": result}})
            counter += 1
        return results

    # otherwise just return the service specification
    return service_spec()


@app.route('/charity/<regno>')
@app.route('/charity/<regno>.<filetype>')
def charity(regno, filetype='html'):
    res = app.config["es"].get(index=app.config["es_index"], doc_type=app.config["es_type"], id=regno, ignore=[404])
    if "_source" in res:
        if filetype == "html":
            return bottle.template('charity', charity=sort_out_date(res["_source"]), charity_id=res["_id"])
        else:
            return res["_source"]
    else:
        bottle.abort(404, bottle.template('Charity {{regno}} not found.', regno=regno))


@app.route('/preview/charity/<regno>')
@app.route('/preview/charity/<regno>.html')
def charity_preview(regno):
    res = app.config["es"].get(index=app.config["es_index"], doc_type=app.config["es_type"], id=regno, ignore=[404])
    if "_source" in res:
        return bottle.template('preview', charity=sort_out_date(res["_source"]), charity_id=res["_id"])
    bottle.abort(404, bottle.template('Charity {{regno}} not found.', regno=regno))


@app.route('/orgid/<orgid>.json')
def orgid_json(orgid):
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
    org = orgid_json(orgid)
    bottle.redirect('/charity/{}'.format(org["id"]))


@app.route('/feeds/ccew.<filetype>')
def ccew_rss(filetype):
    CCEW_URL = 'http://data.charitycommission.gov.uk/'
    res = requests.get(CCEW_URL)
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
        url=CCEW_URL,
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
    return bottle.template('about', this_year=datetime.now().year)


def sort_out_date(charity):
    dates = ["date_registered", "date_removed", "last_modified"]
    for d in dates:
        if d in charity and charity[d]:
            try:
                charity[d] = parser.parse(charity[d])
            except ValueError:
                pass
    return charity


def main():

    parser = argparse.ArgumentParser(description='')  # @TODO fill in

    # server options
    parser.add_argument('-host', '--host', default="localhost", help='host for the server')
    parser.add_argument('-p', '--port', default=8080, help='port for the server')
    parser.add_argument('--debug', action='store_true', dest="debug", help='Debug mode (autoreloads the server)')
    parser.add_argument('--server', default="auto", help='Server backend to use (see http://bottlepy.org/docs/dev/deployment.html#switching-the-server-backend)')

    # elasticsearch options
    parser.add_argument('--es-host', default="localhost", help='host for the elasticsearch instance')
    parser.add_argument('--es-port', default=9200, help='port for the elasticsearch instance')
    parser.add_argument('--es-url-prefix', default='', help='Elasticsearch url prefix')
    parser.add_argument('--es-use-ssl', action='store_true', help='Use ssl to connect to elasticsearch')
    parser.add_argument('--es-index', default='charitysearch', help='index used to store charity data')
    parser.add_argument('--es-type', default='charity', help='type used to store charity data')

    parser.add_argument('--ga-tracking-id', help='Google Analytics Tracking ID')

    args = parser.parse_args()

    app.config["es"] = Elasticsearch(
        host=args.es_host,
        port=args.es_port,
        url_prefix=args.es_url_prefix,
        use_ssl=args.es_use_ssl
    )
    app.config["es_index"] = args.es_index
    app.config["es_type"] = args.es_type
    app.config["ga_tracking_id"] = args.ga_tracking_id

    bottle.debug(args.debug)

    bottle.run(app, server=args.server, host=args.host, port=args.port, reloader=args.debug)

if __name__ == '__main__':
    main()
