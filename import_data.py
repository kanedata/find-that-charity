import csv
import re
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch.exceptions import NotFoundError
import validators
from urllib.parse import urlparse

def parse_postcode(postcode):
    """
    standardises a postcode into the correct format
    """

    if postcode is None:
        return None

    # check for blank/empty
    # put in all caps
    postcode = postcode.strip().upper()
    if postcode=='':
        return None

    # replace any non alphanumeric characters
    postcode = re.sub('[^0-9a-zA-Z]+', '', postcode)

    if postcode=='':
        return None

    # check for nonstandard codes
    if len(postcode)>7:
        return postcode

    first_part = postcode[:-3].strip()
    last_part = postcode[-3:].strip()

    # check for incorrect characters
    first_part = list(first_part)
    last_part = list(last_part)
    if len(last_part)>0 and last_part[0]=="O":
        last_part[0] = "0"

    return "%s %s" % ("".join(first_part), "".join(last_part) )

def fetch_postcode(postcode, es, es_index="postcode", es_type="postcode"):
    if postcode is None:
        return None

    areas = ["hro","wz11","bua11","pct","lsoa11","nuts","msoa11","laua",
             "oa11","ccg","ward","teclec","gor","ttwa","pfa","pcon","lep1",
             "cty","eer","ctry","park","lep2","hlthau","buasd11"]
    try:
        res = es.get(index=es_index, doc_type=es_type, id=postcode, ignore=[404])
        if res['found']:
            return (res['_source'].get("location"),
                    {k:res['_source'].get(k) for k in res['_source'] if k in areas})
    except (NotFoundError, ValueError):
        return None

def parse_company_number(coyno):
    coyno = coyno.strip()
    if coyno=="":
        return None

    if coyno.isdigit():
        return coyno.rjust(8, "0")

    return coyno

def parse_url(url):
    if url is None:
        return None

    url = url.strip()

    if validators.url(url):
        return url

    if validators.url("http://%s" % url):
        return "http://%s" % url

    if url in ["n.a", 'non.e', '.0', '-.-', '.none', '.nil', 'N/A', 'TBC', 'under construction', '.n/a', '0.0', '.P', b'', 'no.website']:
        return None

    for i in ['http;//', 'http//', 'http.//', 'http:\\\\', 'http://http://', 'www://', 'www.http://']:
        url = url.replace(i, 'http://')
    url = url.replace('http:/www', 'http://www')

    for i in ['www,', ':www', 'www:', 'www/', 'www\\\\', '.www']:
        url = url.replace(i, 'www.')

    url = url.replace(',', '.')
    url = url.replace('..', '.')

    if validators.url(url):
        return url

    if validators.url("http://%s" % url):
        return "http://%s" % url

def get_domain(url=None, email=None):
    if url==None:
        return None
    u = urlparse(url)
    domain = u.netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain

def clean_row(row):
    if isinstance(row, dict):
        row = {k: row[k].strip() for k in row}
        for k in row:
            if row[k]=="":
                row[k] = None
    elif isinstance(row, list):
        row = [v.strip() for v in row]
        for k, v in enumerate(row):
            if v=="":
                row[k] = None

    return row

def main():

    parser = argparse.ArgumentParser(description='Import charity data into elasticsearch')

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

    args = parser.parse_args()

    es = Elasticsearch(host=args.es_host, port=args.es_port, url_prefix=args.es_url_prefix, use_ssl=args.es_use_ssl)
    pc_es = None # Elasticsearch postcode instance
    if args.es_pc_host:
        pc_es = Elasticsearch(host=args.es_pc_host, port=args.es_pc_port, url_prefix=args.es_pc_url_prefix, use_ssl=args.es_pc_use_ssl)

    chars = {}

    with open( "data/ccew/extract_charity.csv", "r", encoding="latin1" ) as a:
        csvreader = csv.reader(a, doublequote=False, escapechar='\\')
        ccount = 0
        for row in csvreader:
            if len(row)>1 and row[1]=="0":
                row = clean_row(row)
                char_json = {
                    "_index": args.es_index,
                    "_type": args.es_type,
                    "_op_type": "index",
                    "_id": row[0],
                    "ccew_number": row[0],
                    "oscr_number": None,
                    "active": row[3]=="R",
                    "names": [{"name": row[2], "type": "registered name", "source": "ccew"}],
                    "known_as": row[2],
                    "geo": {
                        "areas": [],
                        "postcode": parse_postcode(row[15]),
                        "location": None
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
                    print('\r' , "[CCEW] %s charities read from extract_charity.csv (main pass)" % ccount, end='')
        print('\r' , "[CCEW] %s charities read from extract_charity.csv (main pass)" % ccount)

        ccount = 0
        a.seek(0)
        for row in csvreader:
            if len(row)>1 and row[1]!="0":
                row = clean_row(row)
                chars[row[0]]["names"].append({"name": row[2], "type": "subsidiary name", "source": "ccew"})
                ccount += 1
                if ccount % 10000 == 0:
                    print('\r' , "[CCEW] %s subsidiaries read from extract_charity.csv (subsidiary pass)" % ccount, end='')
        print('\r' , "[CCEW] %s subsidiaries read from extract_charity.csv (subsidiary pass)" % ccount)

    with open( "data/ccew/extract_main_charity.csv", encoding="latin1") as a:
        csvreader = csv.reader(a, doublequote=False, escapechar='\\')
        ccount = 0
        for row in csvreader:
            if len(row)>1:
                row = clean_row(row)
                if row[1]:
                    chars[row[0]]["company_number"].append({"number": parse_company_number(row[1]), "source": "ccew"})
                if row[9]:
                    chars[row[0]]["url"] = row[9]
                if row[6]:
                    chars[row[0]]["latest_income"] = int(row[6])
                ccount += 1
                if ccount % 10000 == 0:
                    print('\r' , "[CCEW] %s charities read from extract_main_charity.csv" % ccount, end='')
        print('\r' , "[CCEW] %s charities read from extract_main_charity.csv" % ccount)

    with open( "data/ccew/extract_name.csv", encoding="latin1") as a:
        csvreader = csv.reader(a, doublequote=False, escapechar='\\')
        ccount = 0
        for row in csvreader:
            if len(row)>1:
                row = clean_row(row)
                char_names = [i["name"] for i in chars[row[0]]["names"]]
                name = row[3]
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
                    print('\r' , "[CCEW] %s names read from extract_name.csv" % ccount, end='')
        print('\r' , "[CCEW] %s names read from extract_name.csv" % ccount)

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
            row = clean_row(row)

            # check if they're dual registered
            if row["Charity Number"] in dual:
                for c in dual[row["Charity Number"]]:
                    if c in chars:
                        chars[c]["oscr_number"] = row["Charity Number"]
                        char_names = [i["name"] for i in chars[c]["names"]]
                        if row["Charity Name"] not in char_names:
                            chars[c]["names"].append({"name": row["Charity Name"].replace("`","'"), "type": "registered name", "source": "oscr"})
                        if row["Most recent year income"] and chars[c]["latest_income"] is None:
                            chars[c]["latest_income"] = int(row["Most recent year income"])
                        if row["Website"] and chars[c]["url"] is None:
                            chars[c]["url"] = row["Website"]
                        if row["Known As"] and row["Known As"] not in char_names:
                            chars[c]["names"].append({"name": row["Known As"].replace("`","'"), "type": "known as", "source": "oscr"})
                        if chars[c]["geo"]["postcode"] is None and row["Postcode"]:
                            chars[c]["geo"]["postcode"] = parse_postcode( row["Postcode"] )
                        if row["Parent charity number"] \
                            and chars[c]["parent"] is None\
                            and row["Parent charity number"]!=c:
                            chars[c]["parent"] = row["Parent charity number"]
                        cupdated += 1


            # if not dual registered then add as their own record
            else:
                char_json = {
                    "_index": args.es_index,
                    "_type": args.es_type,
                    "_op_type": "index",
                    "_id": row["Charity Number"],
                    "ccew_number": None,
                    "oscr_number": row["Charity Number"],
                    "active": True,
                    "names": [{"name": row["Charity Name"].replace("`","'"), "type": "registered name", "source": "oscr"}],
                    "known_as": row["Charity Name"].replace("`","'"),
                    "geo": {
                        "areas": [],
                        "postcode": row["Postcode"],
                        "location": None
                    },
                    "url": None,
                    "domain": None,
                    "latest_income": None,
                    "company_number": [],
                    "parent": None
                }
                if row["Most recent year income"]:
                    char_json["latest_income"] = int(row["Most recent year income"])
                if row["Website"]:
                    char_json["url"] = row["Website"]
                if row["Known As"]:
                    char_json["names"].append({"name": row["Known As"].replace("`","'"), "type": "known as", "source": "oscr"})
                    char_json["known_as"] = row["Known As"].replace("`","'")
                if row["Parent charity number"]:
                    char_json["parent"] = row["Parent charity number"]

                chars[row["Charity Number"]] = char_json
                cadded +=1
            ccount += 1
            if ccount % 10000 == 0:
                print('\r' , "[OSCR] %s charites added or updated from oscr.csv" % ccount, end='')
        print('\r' , "[OSCR] %s charites added or updated from oscr.csv" % ccount)
        print("[OSCR] %s charites added from oscr.csv" % cadded)
        print("[OSCR] %s charites updated using oscr.csv" % cupdated)

    # @TODO include charity commission register of mergers

    ccount = 0
    for c in chars:
        if pc_es:
            geo_data = fetch_postcode(chars[c]["geo"]["postcode"], pc_es, args.es_pc_index, args.es_pc_type)
            if geo_data:
                chars[c]["geo"]["location"] = geo_data[0]
                chars[c]["geo"]["areas"] = geo_data[1]

        chars[c]["url"] = parse_url(chars[c]["url"])
        chars[c]["domain"] = get_domain(chars[c]["url"])

        chars[c]["alt_names"] = [n["name"] for n in chars[c]["names"] if n["name"]!=chars[c]["known_as"]]

        ccount += 1
        if ccount % 10000 == 0:
            print('\r' , "[Geo] %s charites added location details" % ccount, end='')
    print('\r' , "[Geo] %s charites added location details" % ccount)

    # @TODO capitalisation of names

    print("[elasticsearch] %s charities to save" % len(chars))
    print("[elasticsearch] saving %s charities to %s index" % (len(chars), args.es_index))
    results = bulk(es, list(chars.values()))
    print("[elasticsearch] saved %s charities to %s index" % (results[0], args.es_index))
    print("[elasticsearch] %s errors reported" % len(results[1]) )

if __name__ == '__main__':
    main()
