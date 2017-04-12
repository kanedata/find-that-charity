import csv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

INDEX_NAME = "charitysearch"

def main():

    chars = {}

    with open( "data/ccew/extract_charity.csv", "r", encoding="latin1" ) as a:
        csvreader = csv.reader(a, doublequote=False, escapechar='\\')
        ccount = 0
        for row in csvreader:
            if len(row)>1 and row[1]=="0":
                char_json = {
                    "_index": INDEX_NAME,
                    "_type": "charity",
                    "_op_type": "index",
                    "_id": row[0],
                    "ccew_number": row[0],
                    "oscr_number": None,
                    "active": row[3]=="R",
                    "names": [{"name": row[2].strip(), "type": "registered name", "source": "ccew"}],
                    "known_as": row[2].strip(),
                    "geo": {
                        "areas": [],
                        "postcode": row[15].strip(),
                        "latlng": [None, None]
                    },
                    "url": None,
                    "domain": None,
                    "latest_income": None,
                    "company_number": [],
                    "parent": None
                }
                chars[row[0]] = char_json

                ccount += 1
                if ccount % 10000 == 0:
                    print("[CCEW] %s charities read from extract_charity.csv (main pass)" % ccount)

        ccount = 0
        a.seek(0)
        for row in csvreader:
            if len(row)>1 and row[1]!="0":
                chars[row[0]]["names"].append({"name": row[2].strip(), "type": "subsidiary name", "source": "ccew"})
                ccount += 1
                if ccount % 10000 == 0:
                    print("[CCEW] %s subsidiaries read from extract_charity.csv (subsidiary pass)" % ccount)

    with open( "data/ccew/extract_main_charity.csv", encoding="latin1") as a:
        csvreader = csv.reader(a, doublequote=False, escapechar='\\')
        ccount = 0
        for row in csvreader:
            if len(row)>1:
                if row[1].strip()!="":
                    chars[row[0]]["company_number"].append({"number": row[1], "source": "ccew"})
                if row[9].strip()!="":
                    chars[row[0]]["url"] = row[9]
                if row[6].strip()!="":
                    chars[row[0]]["latest_income"] = int(row[6])
                ccount += 1
                if ccount % 10000 == 0:
                    print("[CCEW] %s charities read from extract_main_charity.csv" % ccount)

    with open( "data/ccew/extract_name.csv", encoding="latin1") as a:
        csvreader = csv.reader(a, doublequote=False, escapechar='\\')
        ccount = 0
        for row in csvreader:
            if len(row)>1:
                char_names = [i["name"] for i in chars[row[0]]["names"]]
                name = row[3].strip()
                if name not in char_names:
                    name_type = "other name"
                    if row[1]!="0":
                        name_type = "other subsidiary name"
                    chars[row[0]]["names"].append({
                        "name": name,
                        "type": name_type,
                        "source": "ccew"
                    })
                ccount += 1
                if ccount % 10000 == 0:
                    print("[CCEW] %s names read from extract_name.csv" % ccount)

    # store dual registration details
    dual = {}
    with open( "data/dual-registered-uk-charities.csv" ) as a:
        csvreader = csv.DictReader(a)
        for row in csvreader:
            if row["Scottish Charity Number"] not in dual:
                dual[row["Scottish Charity Number"]] = []
            dual[row["Scottish Charity Number"]].append(row["E&W Charity Number"])

    # go through the Scottish charities
    with open( "data/oscr.csv", encoding="latin1" ) as a:
        csvreader = csv.DictReader(a)
        ccount = 0
        cadded = 0
        cupdated = 0
        for row in csvreader:

            # check if they're dual registered
            if row["Charity Number"].strip() in dual:
                for c in dual[row["Charity Number"].strip()]:
                    if c in chars:
                        chars[c]["oscr_number"] = row["Charity Number"]
                        char_names = [i["name"] for i in chars[c]["names"]]
                        if row["Charity Name"] not in char_names:
                            chars[c]["names"].append({"name": row["Charity Name"].strip(), "type": "registered name", "source": "oscr"})
                        if row["Most recent year income"].strip()!="" and chars[c]["latest_income"] is None:
                            chars[c]["latest_income"] = int(row["Most recent year income"])
                        if row["Website"].strip()!="" and chars[c]["url"] is None:
                            chars[c]["url"] = row["Website"].strip()
                        if row["Known As"].strip()!="" and row["Known As"] not in char_names:
                            chars[c]["names"].append({"name": row["Known As"].strip(), "type": "known as", "source": "oscr"})
                        if row["Parent charity number"].strip()!="" \
                            and chars[c]["parent"] is None\
                            and row["Parent charity number"]!=c:
                            chars[c]["parent"] = row["Parent charity number"].strip()
                        cupdated += 1


            # if not dual registered then add as their own record
            else:
                char_json = {
                    "_index": INDEX_NAME,
                    "_type": "charity",
                    "_op_type": "index",
                    "_id": row["Charity Number"],
                    "ccew_number": None,
                    "oscr_number": row["Charity Number"],
                    "active": True,
                    "names": [{"name": row["Charity Name"].strip(), "type": "registered name", "source": "oscr"}],
                    "known_as": row["Charity Name"].strip(),
                    "geo": {
                        "areas": [],
                        "postcode": row["Postcode"].strip(),
                        "latlng": [None, None]
                    },
                    "url": None,
                    "domain": None,
                    "latest_income": None,
                    "company_number": [],
                    "parent": None
                }
                if row["Most recent year income"].strip()!="":
                    char_json["latest_income"] = int(row["Most recent year income"])
                if row["Website"].strip()!="":
                    char_json["url"] = row["Website"].strip()
                if row["Known As"].strip()!="":
                    char_json["names"].append({"name": row["Known As"].strip(), "type": "known as", "source": "oscr"})
                    char_json["known_as"] = row["Known As"].strip()
                if row["Parent charity number"].strip()!="":
                    char_json["parent"] = row["Parent charity number"].strip()

                chars[row["Charity Number"]] = char_json
                cadded +=1
            ccount += 1
            if ccount % 10000 == 0:
                print("[OSCR] %s charites added or updated from oscr.csv" % ccount)
    print("[OSCR] %s charites added from oscr.csv" % cadded)
    print("[OSCR] %s charites updated using oscr.csv" % cupdated)

    # @TODO include charity commission register of mergers

    print("[elasticsearch] %s charities to save" % len(chars))
    es = Elasticsearch()
    if es.indices.exists(INDEX_NAME):
        print("[elasticsearch] deleting '%s' index..." % (INDEX_NAME))
        res = es.indices.delete(index = INDEX_NAME)
        print("[elasticsearch] response: '%s'" % (res))
    # since we are running locally, use one shard and no replicas
    print("[elasticsearch] creating '%s' index..." % (INDEX_NAME))
    res = es.indices.create(index = INDEX_NAME)
    print("[elasticsearch] saving %s charities to %s index" % (len(chars), INDEX_NAME))
    results = bulk(es, list(chars.values()))
    print("[elasticsearch] saved %s charities to %s index" % (results[0], INDEX_NAME))
    print("[elasticsearch] %s errors reported" % len(results[1]) )

if __name__ == '__main__':
    main()
