from __future__ import print_function

import argparse
import bottle
from elasticsearch import Elasticsearch

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
    	                                "fields": [ "known_as^3", "alt_names" ]
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
                                    "fields": [ "known_as^3", "alt_names" ],
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
    		            #}, {
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

@app.route('/reconcile')
def reconcile():
    q = bottle.request.query.query
    query = search_query(q)
    res = app.config["es"].search_template(index=app.config["es_index"], doc_type=app.config["es_type"], body=query, ignore=[404])
    return res

@app.route('/charity/<regno>')
@app.route('/charity/<regno>.<filetype>')
def charity(regno, filetype='html'):
    res = app.config["es"].get(index=app.config["es_index"], doc_type=app.config["es_type"], id=regno, ignore=[404])
    if "_source" in res:
        if filetype=="html":
            return bottle.template('charity', charity=res["_source"], charity_id=res["_id"])
        else:
            return res["_source"]


def main():

    parser = argparse.ArgumentParser(description='') # @TODO fill in

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
