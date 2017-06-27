import csv
import time
from elasticsearch import Elasticsearch
es = Elasticsearch()

TEST_FILE = "data/grantnav_test_sample.csv"
MISMATCH_FILE = "data/test_mismatches.csv"
ES_INDEX = "charitysearch"
ES_TYPE = "charity"


def get_test_set():

    with open("data/grantnav.csv", encoding="utf-8") as grantnav:
        with open("data/grantnav_test.csv", "w", encoding="utf-8") as test_file:
            reader = csv.DictReader(grantnav)
            writer = csv.writer(test_file, lineterminator='\r')
            writer.writerow(["charitynumber", "name", "company_number"])
            for grant in reader:
                charitynumber = None
                if grant["Recipient Org:Charity Number"] != "":
                    charitynumber = grant["Recipient Org:Charity Number"].strip().replace("GB-CHC-", "")
                else:
                    if grant["Recipient Org:Identifier"].startswith("GB-CHC-"):
                        charitynumber = grant["Recipient Org:Identifier"].replace("GB-CHC-", "").strip()

                if charitynumber:
                    writer.writerow([charitynumber, grant["Recipient Org:Name"].encode("utf-8").decode("utf-8"), grant["Recipient Org:Company Number"].strip()])


def get_test_sample(sample_size=10000):
    import random
    with open("data/grantnav_test.csv", encoding="utf-8") as test_file:
        with open(TEST_FILE, "w", encoding="utf-8") as sample_file:
            rows = test_file.readlines()
            sample_file.write(rows[0])
            rows = rows[1:]
            rows = random.sample(rows, sample_size)
            for r in rows:
                sample_file.write(r)


def safe_q(q):
    q = q.replace("\\", "\\\\")
    for i in list('+-=&|><!(){}[]^"~*?:/'):
        q = q.replace(i, '\\%s' % i)
    return q


def recon_test_1(name):
    name = safe_q(name)
    res = es.search(index=ES_INDEX, doc_type=ES_TYPE, q=name, ignore=[404])
    if res["hits"]["total"] > 0:
        return res["hits"]["hits"][0]
    # 10000 grants checked
    # Successful matches: 5829 [58%]
    # Mismatches: 4112 [41%]
    # No charity found: 59 [1%]
    # Took 43.1 seconds


def recon_test_2(name):
    name = safe_q(name)
    res = es.search(index=ES_INDEX, doc_type=ES_TYPE, body={"query": {"query_string": {"query": name}}}, ignore=[404])
    if res["hits"]["total"] > 0:
        return res["hits"]["hits"][0]
    # 10000 grants checked
    # Successful matches: 5829 [58%]
    # Mismatches: 4112 [41%]
    # No charity found: 59 [1%]
    # Took 43.0 seconds


def recon_test_3(name):
    name = safe_q(name)
    res = es.search(index=ES_INDEX, doc_type=ES_TYPE, body={"query": {"match": {"known_as": name}}}, ignore=[404])
    if res["hits"]["total"] > 0:
        return res["hits"]["hits"][0]
    # 10000 grants checked
    # Successful matches: 7234 [72%]
    # Mismatches: 2636 [26%]
    # No charity found: 130 [1%]
    # Took 65.8 seconds


def recon_test_4(name):
    name = safe_q(name)
    query = {
        "query": {
            "boosting": {
                "positive": {
                    "query_string": {
                        "query": name
                    }
                },
                "negative": {
                    "term": {
                        "active": False
                    }
                },
                "negative_boost": 0.3
            }
        }
    }
    res = es.search(index=ES_INDEX, doc_type=ES_TYPE, body=query, ignore=[404])
    if res["hits"]["total"] > 0:
        return res["hits"]["hits"][0]
    # 10000 grants checked
    # Successful matches: 6886 [69%]
    # Mismatches: 3055 [31%]
    # No charity found: 59 [1%]
    # Took 64.1 seconds


def recon_test_5(name):
    name = safe_q(name)
    query = {
        "query": {
            "function_score": {
                "query": {
                    "boosting": {
                        "positive": {
                            "query_string": {
                                "query": name
                            }
                        },
                        "negative": {
                            "term": {
                                "active": False
                            }
                        },
                        "negative_boost": 0.3
                    }
                },
                "functions": [
                    {
                        "field_value_factor": {
                            "field": "latest_income",
                            "modifier": "log1p",
                            "missing": 1
                        }
                    }
                ]
            }
        }
    }
    res = es.search(index=ES_INDEX, doc_type=ES_TYPE, body=query, ignore=[404])
    if res["hits"]["total"] > 0:
        return res["hits"]["hits"][0]
    # 10000 grants checked
    # Successful matches: 6579 [66%]
    # Mismatches: 3362 [34%]
    # No charity found: 59 [1%]
    # Took 77.4 seconds


def recon_test_6(name):
    name = safe_q(name)
    query = {
        "query": {
            "function_score": {
                "query": {
                    "boosting": {
                        "positive": {
                            "query_string": {
                                "query": name
                            }
                        },
                        "negative": {
                            "term": {
                                "active": False
                            }
                        },
                        "negative_boost": 0.3
                    }
                },
                "functions": [
                    {
                        "filter": {"match": {"known_as": name}},
                        "weight": 2
                    },
                    {
                        "field_value_factor": {
                            "field": "latest_income",
                            "modifier": "log1p",
                            "missing": 1
                        }
                    }
                ]
            }
        }
    }
    res = es.search(index=ES_INDEX, doc_type=ES_TYPE, body=query, ignore=[404])
    if res["hits"]["total"] > 0:
        return res["hits"]["hits"][0]
    # 10000 grants checked
    # Successful matches: 6531 [65%]
    # Mismatches: 3410 [34%]
    # No charity found: 59 [1%]
    # Took 104.1 seconds


def recon_test_7(name):
    name = safe_q(name)
    query = {
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
            "domain_name": None
        }
    }
    res = es.search_template(index=ES_INDEX, doc_type=ES_TYPE, body=query, ignore=[404])
    if res["hits"]["total"] > 0:
        return res["hits"]["hits"][0]
    # 9534 grants checked
    # Successful matches: 7950 [83%]
    # Mismatches: 1525 [16%]
    # No charity found: 59 [1%]
    # Mean score of matched: 497160
    # Mean score of unmatched: 154078
    # Took 160.2 seconds


def recon_test(*args):
    return recon_test_7(*args)


def main():

    start = time.clock()
    with open(TEST_FILE, encoding="utf-8") as grantnav:
        with open(MISMATCH_FILE, "w", encoding="utf-8") as mismatch_file:
            reader = csv.DictReader(grantnav)
            writer = csv.writer(mismatch_file, lineterminator='\r')
            writer.writerow(["ccnum", "name", "match_ccnum",
                             "match_name", "match_score"])
            counts = {"match": 0, "blank": 0, "not_match": 0,
                      "total": 0, "charity_wrong": 0}
            scores = {"match": [], "not_match": []}
            for grant in reader:
                res = recon_test(grant["name"])
                if counts["total"] % 100 == 0:
                    print("\r{} grants checked".format(counts["total"]), end='')
                if res is None:
                    counts["total"] += 1
                    counts["blank"] += 1
                    continue

                grant["charitynumber"] = grant["charitynumber"].replace(" ", "").upper().replace("SCO", "SC0")
                existing_charity = es.get(index=ES_INDEX, doc_type=ES_TYPE, id=grant["charitynumber"], ignore=[404])
                ccnum = res["_id"]
                if ccnum == grant["charitynumber"]:
                    counts["total"] += 1
                    counts["match"] += 1
                    scores["match"].append(res["_score"])
                elif existing_charity["found"]:
                    counts["total"] += 1
                    counts["not_match"] += 1
                    scores["not_match"].append(res["_score"])
                    writer.writerow([
                        grant["charitynumber"],
                        grant["name"],
                        res["_id"],
                        res["_source"]["known_as"],
                        res["_score"]
                    ])
                else:
                    counts["charity_wrong"] += 1

        print("\r# {} grants checked".format(counts["total"]))
        print("# Successful matches: {} [{:.0%}]".format(counts["match"], counts["match"] / counts["total"]))
        print("# Mismatches: {} [{:.0%}]".format(counts["not_match"], counts["not_match"] / counts["total"]))
        print("# No charity found: {} [{:.0%}]".format(counts["blank"], counts["blank"] / counts["total"]))
        print("# Mean score of matched: {:.0f}".format(sum(scores["match"]) / len(scores["match"])))
        print("# Mean score of unmatched: {:.0f}".format(sum(scores["not_match"]) / len(scores["not_match"])))
        print("# Took {:.1f} seconds".format(time.clock() - start))

if __name__ == '__main__':
    main()
