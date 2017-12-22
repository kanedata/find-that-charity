import csv
import re
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch.exceptions import NotFoundError
import validators
from urllib.parse import urlparse
import argparse
import os
import titlecase


def title_exceptions(word, **kwargs):

    word_test = word.strip("(){}<>.")

    # lowercase words
    if word_test.lower() in ['a', 'an', 'of', 'the', 'is', 'or']:
        return word.lower()

    # uppercase words
    if word_test.upper() in ['UK', 'FM', 'YMCA', 'PTA', 'PTFA',
                             'NHS', 'CIO', 'U3A', 'RAF', 'PFA', 'ADHD',
                             'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI',
                             'AFC', 'CE', 'CIC'
                             ]:
        return word.upper()

    # words with only vowels that aren't all uppercase
    if word_test.lower() in ['st', 'mr', 'mrs', 'ms', 'ltd', 'dr', 'cwm', 'clwb', 'drs']:
        return None

    # words with number ordinals
    ord_numbers_re = re.compile("([0-9]+(?:st|nd|rd|th))")
    if bool(ord_numbers_re.search(word_test.lower())):
        return word.lower()

    # words with dots/etc in the middle
    for s in [".", "'", ")"]:
        dots = word.split(s)
        if(len(dots) > 1):
            # check for possesive apostrophes
            if s == "'" and dots[-1].upper() == "S":
                return s.join([titlecase.titlecase(i, title_exceptions) for i in dots[:-1]] + [dots[-1].lower()])
            # check for you're and other contractions
            if word_test.upper() in ["YOU'RE", "DON'T", "HAVEN'T"]:
                return s.join([titlecase.titlecase(i, title_exceptions) for i in dots[:-1]] + [dots[-1].lower()])
            return s.join([titlecase.titlecase(i, title_exceptions) for i in dots])

    # words with only vowels in (treat as acronyms)
    vowels = re.compile("[AEIOUYaeiouy]")
    if not bool(vowels.search(word_test)):
        return word.upper()

    return None


def parse_name(name):
    if type(name) != str:
        return name

    name = name.strip()

    # if it contains any lowercase letters then return as is
    for c in name:
        if c.islower():
            return name

    # try titlecasing
    try:
        name = titlecase.titlecase(name, title_exceptions)
    except:
        pass

    # Make sure first letter is capitalise
    return name[0].upper() + name[1:]

    



def parse_postcode(postcode):
    """
    standardises a postcode into the correct format
    """

    if postcode is None:
        return None

    # check for blank/empty
    # put in all caps
    postcode = postcode.strip().upper()
    if postcode == '':
        return None

    # replace any non alphanumeric characters
    postcode = re.sub('[^0-9a-zA-Z]+', '', postcode)

    if postcode == '':
        return None

    # check for nonstandard codes
    if len(postcode) > 7:
        return postcode

    first_part = postcode[:-3].strip()
    last_part = postcode[-3:].strip()

    # check for incorrect characters
    first_part = list(first_part)
    last_part = list(last_part)
    if len(last_part) > 0 and last_part[0] == "O":
        last_part[0] = "0"

    return "%s %s" % ("".join(first_part), "".join(last_part))


def fetch_postcode(postcode, es, es_index="postcode", es_type="postcode"):
    if postcode is None:
        return None

    areas = ["hro", "wz11", "bua11", "pct", "lsoa11", "nuts", "msoa11", "laua",
             "oa11", "ccg", "ward", "teclec", "gor", "ttwa", "pfa", "pcon",
             "lep1", "cty", "eer", "ctry", "park", "lep2", "hlthau", "buasd11"]
    try:
        res = es.get(index=es_index, doc_type=es_type,
                     id=postcode, ignore=[404])
        if res['found']:
            return (res['_source'].get("location"),
                    {k: res['_source'].get(k) for
                     k in res['_source'] if k in areas})
    except (NotFoundError, ValueError):
        return None


def parse_company_number(coyno):
    coyno = coyno.strip()
    if coyno == "":
        return None

    if coyno.isdigit():
        return coyno.rjust(8, "0")

    return coyno


def parse_ni_company_number(coyno):
    coyno = coyno.strip()
    if coyno == "" or int(coyno) == 0 or int(coyno) == 999999:
        return None

    if coyno.isdigit():
        return "NI" + coyno.rjust(6, "0")

    return coyno


def parse_ni_charity_number(charno):
    charno = charno.strip()
    if charno.isdigit():
        return "NIC" + charno
    return charno

def add_org_id_prefix(char_json):
    prefixes = []
    if char_json['company_number']:
        for coh in char_json['company_number']:
            prefixes.append('GB-COH-' + coh['number'])
    if char_json['oscr_number']:
        prefixes.append('GB-SC-' + char_json['oscr_number'])
    if char_json['ccew_number']:
        prefixes.append('GB-CHC-' + char_json['ccew_number'])
    if char_json['ccni_number']:
        prefixes.append('GB-NIC-' + char_json['ccni_number'])
    return prefixes

def parse_url(url):
    if url is None:
        return None

    url = url.strip()

    if validators.url(url):
        return url

    if validators.url("http://%s" % url):
        return "http://%s" % url

    if url in ["n.a", 'non.e', '.0', '-.-', '.none', '.nil', 'N/A', 'TBC',
               'under construction', '.n/a', '0.0', '.P', b'', 'no.website']:
        return None

    for i in ['http;//', 'http//', 'http.//', 'http:\\\\',
              'http://http://', 'www://', 'www.http://']:
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
    if url is None:
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
            if row[k] == "":
                row[k] = None
    elif isinstance(row, list):
        row = [v.strip() for v in row]
        for k, v in enumerate(row):
            if v == "":
                row[k] = None

    return row


def import_extract_charity(chars={},
                           datafile=os.path.join("data", "ccew", "extract_charity.csv"),
                           es_index="charitysearch",
                           es_type="charity"):

    with open(datafile, "r", encoding="latin1") as a:
        csvreader = csv.reader(a, doublequote=False, escapechar='\\')
        ccount = 0
        for row in csvreader:
            if len(row) > 1 and row[1] == "0":
                row = clean_row(row)
                char_json = {
                    "_index": es_index,
                    "_type": es_type,
                    "_op_type": "index",
                    "_id": row[0],
                    "ccew_number": row[0],
                    "oscr_number": None,
                    "ccni_number": None,
                    "active": row[3] == "R",
                    "names": [{
                        "name": parse_name(row[2]),
                        "type": "registered name",
                        "source": "ccew"
                    }],
                    "known_as": parse_name(row[2]),
                    "geo": {
                        "areas": [],
                        "postcode": parse_postcode(row[15]),
                        "location": None
                    },
                    "url": None,
                    "domain": None,
                    "latest_income": None,
                    "company_number": [],
                    "parent": None,
                    "ccew_link": "http://apps.charitycommission.gov.uk/Showcharity/RegisterOfCharities/SearchResultHandler.aspx?RegisteredCharityNumber=" + row[0] + "&SubsidiaryNumber=0",
                    "oscr_link": "",
                    "ccni_link": ""
                }

                chars[row[0]] = char_json

                ccount += 1
                if ccount % 10000 == 0:
                    print('\r', "[CCEW] %s charities read from extract_charity.csv (main pass)" % ccount, end='')

        print('\r', "[CCEW] %s charities read from extract_charity.csv (main pass)" % ccount)

        ccount = 0
        a.seek(0)
        for row in csvreader:
            if len(row) > 1 and row[1] != "0":
                row = clean_row(row)
                chars[row[0]]["names"].append({
                    "name": parse_name(row[2]),
                    "type": "subsidiary name",
                    "source": "ccew"
                })
                ccount += 1
                if ccount % 10000 == 0:
                    print('\r', "[CCEW] %s subsidiaries read from extract_charity.csv (subsidiary pass)" % ccount, end='')
        print('\r', "[CCEW] %s subsidiaries read from extract_charity.csv (subsidiary pass)" % ccount)

    return chars


def import_extract_main(chars={}, datafile=os.path.join("data", "ccew", "extract_main_charity.csv")):

    with open(datafile, encoding="latin1") as a:
        csvreader = csv.reader(a, doublequote=False, escapechar='\\')
        ccount = 0
        for row in csvreader:
            if len(row) > 1:
                row = clean_row(row)
                if row[1]:
                    chars[row[0]]["company_number"].append({
                        "number": parse_company_number(row[1]),
                        "url": "http://beta.companieshouse.gov.uk/company/" + parse_company_number(row[1]),
                        "source": "ccew"
                    })
                if row[9]:
                    chars[row[0]]["url"] = row[9]
                if row[6]:
                    chars[row[0]]["latest_income"] = int(row[6])
                ccount += 1
                if ccount % 10000 == 0:
                    print('\r', "[CCEW] %s charities read from extract_main_charity.csv" % ccount, end='')
        print('\r', "[CCEW] %s charities read from extract_main_charity.csv" % ccount)

    return chars


def import_extract_name(chars={}, datafile=os.path.join("data", "ccew", "extract_name.csv")):

    with open(datafile, encoding="latin1") as a:
        csvreader = csv.reader(a, doublequote=False, escapechar='\\')
        ccount = 0
        for row in csvreader:
            if len(row) > 1:
                row = clean_row(row)
                char_names = [i["name"] for i in chars[row[0]]["names"]]
                name = row[3]
                if name not in char_names:
                    try:
                        name = parse_name(name)
                    except:
                        pass
                    name_type = "other name"
                    if row[1] != "0":
                        name_type = "other subsidiary name"
                    chars[row[0]]["names"].append({
                        "name": name,
                        "type": name_type,
                        "source": "ccew"
                    })
                ccount += 1
                if ccount % 10000 == 0:
                    print('\r', "[CCEW] %s names read from extract_name.csv" % ccount, end='')
        print('\r', "[CCEW] %s names read from extract_name.csv" % ccount)

    return chars


def import_dual_reg(datafile=os.path.join("data", "dual-registered-uk-charities.csv")):

    # store dual registration details
    dual = {}
    with open(datafile) as a:
        csvreader = csv.DictReader(a)
        for row in csvreader:
            if row["Scottish Charity Number"] not in dual:
                dual[row["Scottish Charity Number"]] = []
            dual[row["Scottish Charity Number"]].append(row["E&W Charity Number"])

    return dual


def import_oscr(chars={},
                dual={},
                datafile=os.path.join("data", "oscr.csv"),
                es_index="charitysearch",
                es_type="charity"):

    # go through the Scottish charities
    with open(datafile, encoding="latin1") as a:
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
                            chars[c]["names"].append({
                                "name": row["Charity Name"].replace("`", "'"),
                                "type": "registered name",
                                "source": "oscr"
                            })
                        if row["Most recent year income"] and chars[c]["latest_income"] is None:
                            chars[c]["latest_income"] = int(row["Most recent year income"])
                        if row["Website"] and chars[c]["url"] is None:
                            chars[c]["url"] = row["Website"]
                        if row["Known As"] and row["Known As"] not in char_names:
                            chars[c]["names"].append({
                                "name": row["Known As"].replace("`", "'"),
                                "type": "known as",
                                "source": "oscr"
                            })
                        if chars[c]["geo"]["postcode"] is None and row["Postcode"]:
                            chars[c]["geo"]["postcode"] = parse_postcode(row["Postcode"])
                        if row["Parent charity number"] \
                            and chars[c]["parent"] is None\
                            and row["Parent charity number"] != c:
                                chars[c]["parent"] = row["Parent charity number"]
                        cupdated += 1

            # if not dual registered then add as their own record
            else:
                char_json = {
                    "_index": es_index,
                    "_type": es_type,
                    "_op_type": "index",
                    "_id": row["Charity Number"],
                    "ccew_number": None,
                    "oscr_number": row["Charity Number"],
                    "ccni_number": None,
                    "active": True,
                    "names": [{
                        "name": row["Charity Name"].replace("`", "'"),
                        "type": "registered name",
                        "source": "oscr"
                    }],
                    "known_as": row["Charity Name"].replace("`", "'"),
                    "geo": {
                        "areas": [],
                        "postcode": row["Postcode"],
                        "location": None
                    },
                    "url": None,
                    "domain": None,
                    "latest_income": None,
                    "company_number": [],
                    "parent": None,
                    "ccew_link": "",
                    "oscr_link": "http://www.oscr.org.uk/charities/search-scottish-charity-register/charity-details?number=" + row["Charity Number"],
                    "ccni_link": ""
                }
                if row["Most recent year income"]:
                    char_json["latest_income"] = int(row["Most recent year income"])
                if row["Website"]:
                    char_json["url"] = row["Website"]
                if row["Known As"]:
                    char_json["names"].append({
                        "name": row["Known As"].replace("`", "'"),
                        "type": "known as",
                        "source": "oscr"
                    })
                    char_json["known_as"] = row["Known As"].replace("`", "'")
                if row["Parent charity number"]:
                    char_json["parent"] = row["Parent charity number"]

                chars[row["Charity Number"]] = char_json
                cadded += 1
            ccount += 1
            if ccount % 10000 == 0:
                print('\r', "[OSCR] %s charities added or updated from oscr.csv" % ccount, end='')

        print('\r', "[OSCR] %s charities added or updated from oscr.csv" % ccount)
        print('\r', "[OSCR] %s charities added from oscr.csv" % cadded)
        print('\r', "[OSCR] %s charities updated using oscr.csv" % cupdated)

    return chars


def import_ccni(chars={},
                dual={},
                datafile=os.path.join("data", "ccni.csv"),
                extra_names=os.path.join("data", "ccni_extra_names.csv"),
                es_index="charitysearch",
                es_type="charity"):

    # store dual registration details
    ccni_extra = {}
    with open(extra_names, encoding="utf-8") as a:
        csvreader = csv.DictReader(a)
        for row in csvreader:
            if row["Charity_number"] not in ccni_extra:
                ccni_extra[row["Charity_number"]] = []
            for n in row["Other_names"].split(";"):
                ccni_extra[row["Charity_number"]].append(n.strip())

    # go through the Northern Irish charities
    with open(datafile, encoding="utf-8") as a:
        csvreader = csv.DictReader(a)
        ccount = 0
        cadded = 0
        cupdated = 0
        for row in csvreader:
            row = clean_row(row)

            # check if they're dual registered
            if row["Reg charity number"] in dual:
                break
            #     for c in dual[row["Reg charity number"]]:
            #         if c in chars:
            #             chars[c]["ccni_number"] = row["Reg charity number"]
            #             char_names = [i["name"] for i in chars[c]["names"]]
            #             if row["Charity name"] not in char_names:
            #                 chars[c]["names"].append({"name": row["Charity name"].replace("`","'"), "type": "registered name", "source": "ccni"})
            #             if row["Total income"] and chars[c]["latest_income"] is None:
            #                 chars[c]["latest_income"] = int(row["Total income"])
            #             if row["Website"] and chars[c]["url"] is None:
            #                 chars[c]["url"] = row["Website"]
            #             # if row["Known As"] and row["Known As"] not in char_names:
            #             #     chars[c]["names"].append({"name": row["Known As"].replace("`","'"), "type": "known as", "source": "oscr"})
            #             # if chars[c]["geo"]["postcode"] is None and row["Postcode"]:
            #             #     chars[c]["geo"]["postcode"] = parse_postcode( row["Postcode"] )
            #             # if row["Parent charity number"] \
            #             #     and chars[c]["parent"] is None\
            #             #     and row["Parent charity number"]!=c:
            #             #     chars[c]["parent"] = row["Parent charity number"]
            #             cupdated += 1

            # if not dual registered then add as their own record
            else:
                char_json = {
                    "_index": es_index,
                    "_type": es_type,
                    "_op_type": "index",
                    "_id": parse_ni_charity_number(row["Reg charity number"]),
                    "ccew_number": None,
                    "oscr_number": None,
                    "ccni_number": row["Reg charity number"],
                    "active": row["Status"] != "Removed",
                    "names": [{
                        "name": row["Charity name"].replace("`", "'"),
                        "type": "registered name",
                        "source": "ccni"
                    }],
                    "known_as": row["Charity name"].replace("`", "'"),
                    "geo": {
                        "areas": [],
                        "postcode": re.sub(".*,\s", "", row["Public address"]),
                        "location": None
                    },
                    "url": None,
                    "domain": None,
                    "latest_income": None,
                    "company_number": [],
                    "parent": None,
                    "ccew_link": "",
                    "oscr_link": "",
                    "ccni_link": "http://www.charitycommissionni.org.uk/charity-details/?regid=" + row["Reg charity number"] + "&subid=" + row["Sub charity number"]
                }
                if row["Total income"]:
                    char_json["latest_income"] = int(row["Total income"])
                if row["Website"]:
                    char_json["url"] = row["Website"]
                if row["Company number"] is not None and parse_ni_company_number(row["Company number"]) is not None:
                    char_json["company_number"].append({
                        "number": parse_ni_company_number(row["Company number"]),
                        "url": "http://beta.companieshouse.gov.uk/company/" + parse_ni_company_number(row["Company number"]),
                        "source": "ccni"
                    })

                if row["Reg charity number"] in ccni_extra:
                    for name in ccni_extra[row["Reg charity number"]]:
                        char_json["names"].append({
                            "name": name.replace("`", "'"),
                            "type": "known as",
                            "source": "ccni"
                        })
                # if row["Parent charity number"]:
                #     char_json["parent"] = row["Parent charity number"]

                chars[row["Reg charity number"]] = char_json
                cadded += 1

            ccount += 1
            if ccount % 10000 == 0:
                print('\r', "[CCNI] %s charities added or updated from ccni.csv" % ccount, end='')
        print('\r', "[CCNI] %s charities added or updated from ccni.csv" % ccount)
        print('\r', "[CCNI] %s charities added from ccni.csv" % cadded)
        print('\r', "[CCNI] %s charities updated using ccni.csv" % cupdated)

    return chars


def clean_chars(chars={}, pc_es=None, es_pc_index="postcode", es_pc_type="postcode"):

    ccount = 0
    for c in chars:
        if pc_es:
            geo_data = fetch_postcode(chars[c]["geo"]["postcode"], pc_es, es_pc_index, es_pc_type)
            if geo_data:
                chars[c]["geo"]["location"] = geo_data[0]
                chars[c]["geo"]["areas"] = geo_data[1]

        chars[c]["url"] = parse_url(chars[c]["url"])
        chars[c]["domain"] = get_domain(chars[c]["url"])
        chars[c]['org-ids'] = add_org_id_prefix(chars[c])

        chars[c]["alt_names"] = [n["name"] for n in chars[c]["names"] if n["name"] != chars[c]["known_as"]]

        # @TODO capitalisation of names

        ccount += 1
        if ccount % 10000 == 0:
            print('\r', "[Geo] %s charites added location details" % ccount, end='')
    print('\r', "[Geo] %s charites added location details" % ccount)

    return chars


def save_to_elasticsearch(chars, es, es_index):

    print('\r', "[elasticsearch] %s charities to save" % len(chars))
    print('\r', "[elasticsearch] saving %s charities to %s index" % (len(chars), es_index))
    results = bulk(es, list(chars.values()))
    print('\r', "[elasticsearch] saved %s charities to %s index" % (results[0], es_index))
    print('\r', "[elasticsearch] %s errors reported" % len(results[1]))


def main():

    parser = argparse.ArgumentParser(description='Import charity data into elasticsearch')

    parser.add_argument('--folder', type='str', default='data',
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

    args = parser.parse_args()

    es = Elasticsearch(host=args.es_host, port=args.es_port, url_prefix=args.es_url_prefix, use_ssl=args.es_use_ssl)

    potential_env_vars = [
        "ELASTICSEARCH_URL",
        "ES_URL",
        "BONSAI_URL"
    ]
    for e_v in potential_env_vars:
        if os.environ.get(e_v):
            es = Elasticsearch(e_v)
            break

    if not es.ping():
        raise ValueError("Elasticsearch connection failed")

    pc_es = None  # Elasticsearch postcode instance
    if args.es_pc_host:
        pc_es = Elasticsearch(host=args.es_pc_host, port=args.es_pc_port, url_prefix=args.es_pc_url_prefix, use_ssl=args.es_pc_use_ssl)
        if not pc_es.ping():
            raise ValueError("Connection failed - postcode elasticsearch")

    data_files = {
        "extract_charity": os.path.join(args.folder, "ccew", "extract_charity.csv"),
        "extract_main": os.path.join(args.folder, "ccew", "extract_main_charity.csv"),
        "extract_names": os.path.join(args.folder, "ccew", "extract_name.csv"),
        "dual_registration": os.path.join(args.folder, "dual-registered-uk-charities.csv"),
        "oscr": os.path.join(args.folder, "oscr.csv"),
        "ccni": os.path.join(args.folder, "ccni.csv"),
        "ccni_extra_names": os.path.join(args.folder, "ccni_extra_names.csv"),
    }

    chars = import_extract_charity({}, datafile=data_files["extract_charity"], es_index=args.es_index, es_type=args.es_type)
    chars = import_extract_main(chars, datafile=data_files["extract_main"])
    chars = import_extract_name(chars, datafile=data_files["extract_names"])
    dual = import_dual_reg(data_files["dual_registration"])
    chars = import_oscr(chars, dual=dual, datafile=data_files["oscr"], es_index=args.es_index, es_type=args.es_type)
    chars = import_ccni(chars, dual=dual, datafile=data_files["ccni"], extra_names=data_files["ccni_extra_names"], es_index=args.es_index, es_type=args.es_type)
    # @TODO include charity commission register of mergers
    chars = clean_chars(chars, pc_es, args.es_pc_index, args.es_pc_type)
    save_to_elasticsearch(chars, es, args.es_index)

if __name__ == '__main__':
    main()
