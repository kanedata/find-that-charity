import argparse
from elasticsearch import Elasticsearch


INDEXES = [
    {
        "name": "charitysearch",
        "mapping": (
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
                    }
                }
            }
        )
    }
]

def main():

    parser = argparse.ArgumentParser(description='Setup elasticsearch indexes.')
    parser.add_argument('--reset', action='store_true',
                        help='If set, any existing indexes will be deleted and recreated.')
    args = parser.parse_args()

    es = Elasticsearch()

    for i in INDEXES:
        if es.indices.exists( i["name"]  ) and args.reset:
            print("[elasticsearch] deleting '%s' index..." % ( i["name"]  ))
            res = es.indices.delete(index =  i["name"]  )
            print("[elasticsearch] response: '%s'" % (res))
        if not es.indices.exists( i["name"]  ):
            print("[elasticsearch] creating '%s' index..." % ( i["name"]  ))
            res = es.indices.create(index =  i["name"]  )

        if "mapping" in i:
            res = es.indices.put_mapping(i["mapping"][0], i["mapping"][1], index= i["name"]   )
            print("[elasticsearch] set mapping on %s index" % ( i["name"]  ))

if __name__ == '__main__':
    main()
