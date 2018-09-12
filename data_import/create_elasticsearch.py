import argparse
from elasticsearch import Elasticsearch
import os


INDEXES = [
    {
        "name": "charitysearch",
        "mapping": [
            "charity", {
                "properties": {
                    "geo": {
                        "properties": {
                            "location": {
                                "type": "geo_point"
                            }
                        }
                    },
                    "names": {
                        "type": "nested",
                        "properties": {
                            "type": {"type": "string"},
                            "source": {"type": "string"},
                            "name": {"type": "string"}
                        }
                    },
                    "complete_names": {
                        "type": "completion"
                    }
                }
            }
        ]
    }
]


def main():

    parser = argparse.ArgumentParser(description='Setup elasticsearch indexes.')
    parser.add_argument('--reset', action='store_true',
                        help='If set, any existing indexes will be deleted and recreated.')

    # elasticsearch options
    parser.add_argument('--es-host', default="localhost", help='host for the elasticsearch instance')
    parser.add_argument('--es-port', default=9200, help='port for the elasticsearch instance')
    parser.add_argument('--es-url-prefix', default='', help='Elasticsearch url prefix')
    parser.add_argument('--es-use-ssl', action='store_true', help='Use ssl to connect to elasticsearch')
    parser.add_argument('--es-index', default='charitysearch', help='index used to store charity data')
    parser.add_argument('--es-type', default='charity', help='type used to store charity data')

    args = parser.parse_args()

    es = Elasticsearch(host=args.es_host, port=args.es_port, url_prefix=args.es_url_prefix, use_ssl=args.es_use_ssl)

    potential_env_vars = [
        "ELASTICSEARCH_URL",
        "ES_URL",
        "BONSAI_URL"
    ]
    for e_v in potential_env_vars:
        if os.environ.get(e_v):
            es = Elasticsearch(os.environ.get(e_v))
            break

    INDEXES[0]["name"] = args.es_index
    INDEXES[0]["mapping"][0] = args.es_type

    for i in INDEXES:
        if es.indices.exists(i["name"]) and args.reset:
            print("[elasticsearch] deleting '%s' index..." % (i["name"]))
            res = es.indices.delete(index=i["name"])
            print("[elasticsearch] response: '%s'" % (res))
        if not es.indices.exists(i["name"]):
            print("[elasticsearch] creating '%s' index..." % (i["name"]))
            res = es.indices.create(index=i["name"])

        if "mapping" in i:
            res = es.indices.put_mapping(i["mapping"][0], i["mapping"][1], index=i["name"])
            print("[elasticsearch] set mapping on %s index" % (i["name"]))

if __name__ == '__main__':
    main()
