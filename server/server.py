from __future__ import print_function

import argparse
import bottle
import json
from elasticsearch import Elasticsearch
from collections import OrderedDict

app = bottle.default_app()


def search_query(name, domain_name=None):
    return {
        "inline": {
            "query": {
                "function_score": {
                    "query": {
                        "dis_max": {
                            "queries": [
                                {
                                    "multi_match": {
                                        "query": "{{name}}",
                                        "fields": ["known_as^3", "alt_names"]
                                    }
                                }, {
                                    "match_phrase": {
                                        "known_as": "{{name}}"
                                    }
                                # }, {
                                #     "match": {
                                #         "domain": "{{domain_name}}"
                                #     }
                                }
                            ]
                        }
                    },
                    "functions": [
                        {
                            "filter": {"match_phrase_prefix": {"known_as": "{{name}}"}},
                            "weight": 200
                        }, {
                            "filter": {
                                "multi_match": {
                                    "query": "{{name}}",
                                    "fields": ["known_as^3", "alt_names"],
                                    "operator": "and"
                                }
                            },
                            "weight": 10
                        }, {
                        #     "filter": {"match_phrase_prefix": {"alt_names": "{{name}}"}},
                        #     "weight": 100
                        # }, {
                        # 	"filter": {"term": {"domain": "{{domain_name}}"}},
                        # 	"weight": 50
                        # }, {
                            "filter": {"term": {"active": False}},
                            "weight": 0.9
                        }, {
                            "field_value_factor": {
                                "field": "latest_income",
                                "modifier": "log2p",
                                "missing": 1
                            }
                        }
                    ]
                }
            }
        },
        "params": {
            "name": name,
            "domain_name": domain_name
        }
    }


def esdoc_orresponse(query):
    """Decorate the elasticsearch document to the OpenRefine response API

    Specification found here: https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation-Service-API#service-metadata
    """
    res = app.config["es"].search_template(index=app.config["es_index"], doc_type=app.config["es_type"], body=query, ignore=[404])
    print(res)
    res["hits"]["result"] = res["hits"].pop("hits")
    for i in res["hits"]["result"]:
        i["id"] = i.pop("_id")
        i["type"] = [i.pop("_type")]
        i["score"] = i.pop("_score")
        i["index"] = i.pop("_index")
        i["source"] = i.pop("_source")
        i["name"] = i["source"]["known_as"]
        if i["name"] == query["params"]["name"] and i["score"] == res["hits"]["max_score"]:
            i["match"] = True
        else:
            i["match"] = False
    return res["hits"]


def service_spec():
        """Return the default service specification

        Specification found here: https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation-Service-API#service-metadata
        """
        service_url = "http://localhost:8080/"

        return {
            "name": app.config["es_index"],
            "identifierSpace": "http://rdf.freebase.com/ns/type.object.id",
            "schemaSpace": "http://rdf.freebase.com/ns/type.object.id",
            "view": {
                "url": service_url + "charity/{{id}}"
            },
            "preview": {
                "url": service_url + "preview/charity/{{id}}",
                "width": 430,
                "height": 300
            },
            "defaultTypes": [{
                "id": "/" + app.config["es_type"],
                "name": app.config["es_type"]
            }]
        }


@app.route('/reconcile')
@app.post('/reconcile')
def reconcile():
    """ Index of the server. If ?query or ?queries used then search,
                otherwise return the default response as JSON
    """
    query = search_query(bottle.request.query.query) or None
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
            result = esdoc_orresponse(search_query(queries_json[q]["query"]))["result"]
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
            return bottle.template('charity', charity=res["_source"], charity_id=res["_id"])
        else:
            return res["_source"]
    else:
        bottle.abort(404, bottle.template('Charity {{regno}} not found.', regno=regno))


@app.route('/preview/charity/<regno>')
@app.route('/preview/charity/<regno>.html')
def charity(regno):
    res = app.config["es"].get(index=app.config["es_index"], doc_type=app.config["es_type"], id=regno, ignore=[404])
    if "_source" in res:
        return bottle.template('preview', charity=res["_source"], charity_id=res["_id"])
    else:
        bottle.abort(404, bottle.template('Charity {{regno}} not found.', regno=regno))


def main():

    parser = argparse.ArgumentParser(description='')  # @TODO fill in

    # server options
    parser.add_argument('-host', '--host', default="localhost", help='host for the server')
    parser.add_argument('-p', '--port', default=8080, help='port for the server')
    parser.add_argument('--debug', action='store_true', dest="debug", help='Debug mode (autoreloads the server)')

    # elasticsearch options
    parser.add_argument('--es-host', default="localhost", help='host for the elasticsearch instance')
    parser.add_argument('--es-port', default=9200, help='port for the elasticsearch instance')
    parser.add_argument('--es-url-prefix', default='', help='Elasticsearch url prefix')
    parser.add_argument('--es-use-ssl', action='store_true', help='Use ssl to connect to elasticsearch')
    parser.add_argument('--es-index', default='charitysearch', help='index used to store charity data')
    parser.add_argument('--es-type', default='charity', help='type used to store charity data')

    args = parser.parse_args()

    app.config["es"] = Elasticsearch(host=args.es_host, port=args.es_port, url_prefix=args.es_url_prefix, use_ssl=args.es_use_ssl)
    app.config["es_index"] = args.es_index
    app.config["es_type"] = args.es_type

    bottle.debug(args.debug)

    bottle.run(app, host=args.host, port=args.port, reloader=args.debug)

if __name__ == '__main__':
    main()
