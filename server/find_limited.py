import csv
from elasticsearch import Elasticsearch


def main():

    es = Elasticsearch()

    with open("data/ccew/extract_charity.csv", "r", encoding="latin1") as a:
        csvreader = csv.reader(a, doublequote=False, escapechar='\\')
        ccount = 0
        for row in csvreader:
            if len(row) > 1 and row[1] == "0":
                name = row[2].strip()
                limited_name = name + " LIMITED"
                # res = es.search(index="charitysearch", doc_type='charity', body={"query": {"bool": {"must": [{"match": {"known_as": limited_name}}]}}}, ignore=[404])
                res = es.search(index="charitysearch", doc_type='charity', body={"query": {"term": {"known_as": limited_name}}}, ignore=[404])
                if res["hits"]["total"] == 1:
                    print(res["hits"]["hits"][0]["_source"]["known_as"], name)

if __name__ == '__main__':
    main()
