import argparse
import os
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from import_data import clean_char, save_to_elasticsearch


def main():

    parser = argparse.ArgumentParser(description='Reindex charity data into elasticsearch')

    parser.add_argument('--folder', type=str, default='data',
                        help='Root path of the data folder.')

    # elasticsearch options
    parser.add_argument('--es-host', default="localhost", help='host for the elasticsearch instance')
    parser.add_argument('--es-port', default=9200, help='port for the elasticsearch instance')
    parser.add_argument('--es-url-prefix', default='', help='Elasticsearch url prefix')
    parser.add_argument('--es-use-ssl', action='store_true', help='Use ssl to connect to elasticsearch')
    parser.add_argument('--es-index', default='charitysearch', help='index used to store charity data')
    parser.add_argument('--es-type', default='charity', help='type used to store charity data')

    # elasticsearch postcode options
    parser.add_argument('--es-pc-host', default=None, help='host for the postcode elasticsearch instance')
    parser.add_argument('--es-pc-port', default=9200, help='port for the postcode elasticsearch instance')
    parser.add_argument('--es-pc-url-prefix', default='', help='Postcode elasticsearch url prefix')
    parser.add_argument('--es-pc-use-ssl', action='store_true', help='Use ssl to connect to postcode elasticsearch')
    parser.add_argument('--es-pc-index', default='postcode', help='index used to store postcode data')
    parser.add_argument('--es-pc-type', default='postcode', help='type used to store postcode data')

    parser.add_argument('--debug', action='store_true', help='Only load first 10000 rows for ccew')

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

    if not es.ping():
        raise ValueError("Elasticsearch connection failed")

    pc_es = None  # Elasticsearch postcode instance
    if args.es_pc_host:
        pc_es = Elasticsearch(host=args.es_pc_host, port=args.es_pc_port, url_prefix=args.es_pc_url_prefix, use_ssl=args.es_pc_use_ssl)
        if not pc_es.ping():
            raise ValueError("Connection failed - postcode elasticsearch")
            
    res = scan(es, index=args.es_index, doc_type=args.es_type)
    chars = {}
    for r in res:
        char = {
            **r["_source"], 
            "_index": r["_index"],
            "_type": r["_type"],
            "_op_type": "index",
            "_id": r["_id"],
        }
        chars[r["_id"]] = clean_char(char)
        if len(chars) % 10000 == 0:
            print('\r', "[Fetch] %s charites fetched from index" % len(chars), end='')
    print('\r', "[Fetch] %s charites fetched from index" % len(chars))

    if args.debug:
        import random
        import json
        random_keys = random.choices(list(chars.keys()), k=10)
        for r in random_keys:
            print(r, chars[r])
    
    save_to_elasticsearch(chars, es, args.es_index)

if __name__ == '__main__':
    main()
