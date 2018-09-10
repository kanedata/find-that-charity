"""
Run the find that charity server
"""
from __future__ import print_function
import os
import argparse
import json
from collections import OrderedDict
import time
from datetime import datetime, timezone
import csv
import io

from dateutil import parser
import yaml
import bottle
from elasticsearch import Elasticsearch
import requests
from bs4 import BeautifulSoup

app = bottle.default_app()

# everywhere gives a different env var for elasticsearch services...
POTENTIAL_ENV_VARS = [
    "ELASTICSEARCH_URL",
    "ES_URL",
    "BONSAI_URL"
]
for e_v in POTENTIAL_ENV_VARS:
    if os.environ.get(e_v):
        app.config["es"] = Elasticsearch(os.environ.get(e_v))
        app.config["es_index"] = 'charitysearch'
        app.config["es_type"] = 'charity'
        break

if os.environ.get("GA_TRACKING_ID"):
    app.config["ga_tracking_id"] = os.environ.get("GA_TRACKING_ID")

if os.environ.get("ADMIN_PASSWORD"):
    app.config["admin_password"] = os.environ.get("ADMIN_PASSWORD")


app.config["csv_options"] = {
    "file_encoding": ("File encoding", {
        "utf8": "UTF-8",
        "utf16": "UTF-16",
        "ascii": "ASCII",
        "latin1": "latin1"
    }),
    "delimiter": ("CSV Field delimiter", {
        ",": ", (comma)",
        ";": "; (semi-colon)",
        "\t": "Tab-delimited",
        "|": "| (pipe)",
        "^": "^ (caret)",
    }),
    "quotechar": ("Quote Character", {
        "\"": '" (double quote)',
        "'": "' (single quote)",
        "~": "~ (tilde)",
    }),
    "escapechar": ("Escape Character", {
        "": 'No escape character',
        "\\": '\\ (backslash)',
    }),
    "doublequote": ("Double quoting", {
        "1": 'Doubled quoting',
        "0": 'No double quoting',
    }),
    "quoting": ("When quotes are used", {
        csv.QUOTE_MINIMAL: "Only when special characters used",
        csv.QUOTE_ALL: "All fields quoted",
        csv.QUOTE_NONNUMERIC: "All non-numeric fields quoted",
        csv.QUOTE_NONE: "No fields quoted",
    })
}

def search_query(term):
    """
    Fetch the search query and insert the query term
    """
    with open('./es_config.yml', 'rb') as yaml_file:
        json_q = yaml.load(yaml_file)
        for param in json_q["params"]:
            json_q["params"][param] = term
        return json.dumps(json_q)


def recon_query(term):
    """
    Fetch the reconciliation query and insert the query term
    """
    with open('./recon_config.yml', 'rb') as yaml_file:
        json_q = yaml.load(yaml_file)
        for param in json_q["params"]:
            json_q["params"][param] = term
        return json.dumps(json_q)


def esdoc_orresponse(query):
    """Decorate the elasticsearch document to the OpenRefine response API

    Specification found here: https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation-Service-API#service-metadata
    """
    res = app.config["es"].search_template(
        index=app.config["es_index"],
        doc_type=app.config["es_type"],
        body=query,
        ignore=[404]
    )
    res["hits"]["result"] = res["hits"].pop("hits")
    for i in res["hits"]["result"]:
        i["id"] = i.pop("_id")
        i["type"] = [i.pop("_type")]
        i["score"] = i.pop("_score")
        i["index"] = i.pop("_index")
        i["source"] = i.pop("_source")
        i["name"] = i["source"]["known_as"] + " (" + i["id"] + ")"
        if not i["source"]["active"]:
            i["name"] += " [INACTIVE]"
        if i["source"]["known_as"].lower() == json.loads(query)["params"]["name"].lower() and i["score"] == res["hits"]["max_score"]:
            i["match"] = True
        else:
            i["match"] = False
    return res["hits"]


def service_spec():
    """Return the default service specification

    Specification found here: https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation-Service-API#service-metadata
    """
    service_url = "{}://{}".format(
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc,
    )
    return {
        "name": app.config["es_index"],
        "identifierSpace": "http://rdf.freebase.com/ns/type.object.id",
        "schemaSpace": "http://rdf.freebase.com/ns/type.object.id",
        "view": {
            "url": service_url + "/charity/{{id}}"
        },
        "preview": {
            "url": service_url + "/preview/charity/{{id}}",
            "width": 430,
            "height": 300
        },
        "defaultTypes": [{
            "id": "/" + app.config["es_type"],
            "name": app.config["es_type"]
        }]
    }


def search_return(query):
    """
    Fetch search results and display on a template
    """
    res = app.config["es"].search_template(
        index=app.config["es_index"],
        doc_type=app.config["es_type"],
        body=query,
        ignore=[404]
    )
    res = res["hits"]
    for result in res["hits"]:
        result["_link"] = "/charity/" + result["_id"]
        result["_source"] = sort_out_date(result["_source"])
    return bottle.template('search', res=res, term=json.loads(query)["params"]["name"])


def check_password(_, passwd):
    if passwd == app.config["admin_password"]:
        return True


@app.route('/')
def home():
    """
    Get the index page for the site
    """
    query = bottle.request.query.get('q')
    if query:
        query = search_query(query)
        return search_return(query)
    return bottle.template('index', term='')


@app.route('/random')
@app.route('/random.<filetype>')
def random(filetype="html"):
    """ Get a random charity record
    """
    query = {
        "size": 1,
        "query": {
            "function_score": {
                "functions": [
                    {
                        "random_score": {
                            "seed": str(time.time())
                        }
                    }
                ]
            }
        }
    }

    if "active" in bottle.request.query:
        query["query"]["function_score"]["query"] = {"match": {"active": True}}

    res = app.config["es"].search(
        index=app.config["es_index"],
        doc_type=app.config["es_type"],
        body=query,
        ignore=[404]
    )
    char = None
    if "hits" in res:
        if "hits" in res["hits"]:
            char = res["hits"]["hits"][0]

    if char:
        if filetype == "html":
            bottle.redirect("/charity/{}".format(char["_id"]))
        return char["_source"]



@app.route('/reconcile')
@app.post('/reconcile')
def reconcile():
    """ Index of the server. If ?query or ?queries used then search,
                otherwise return the default response as JSON
    """
    query = recon_query(bottle.request.query.query) or None
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
            query_id = "q" + str(counter)
            # print(queries_json[q], queries_json[q]["query"])
            result = esdoc_orresponse(recon_query(
                queries_json[query_id]["query"]))["result"]
            results.update({query_id: {"result": result}})
            counter += 1
        return results

    # otherwise just return the service specification
    return service_spec()


@app.route('/charity/<regno>')
@app.route('/charity/<regno>.<filetype>')
def charity(regno, filetype='html'):
    """
    Return a single charity record
    """
    res = app.config["es"].get(index=app.config["es_index"], doc_type=app.config["es_type"], id=regno, ignore=[404])
    if "_source" in res:
        if filetype == "html":
            return bottle.template('charity', charity=sort_out_date(res["_source"]), charity_id=res["_id"])
        return res["_source"]
    else:
        bottle.abort(404, bottle.template('Charity {{regno}} not found.', regno=regno))


@app.route('/preview/charity/<regno>')
@app.route('/preview/charity/<regno>.html')
def charity_preview(regno):
    """
    Small version of charity record

    Used in reconciliation API
    """
    res = app.config["es"].get(index=app.config["es_index"], doc_type=app.config["es_type"], id=regno, ignore=[404])
    if "_source" in res:
        return bottle.template('preview', charity=sort_out_date(res["_source"]), charity_id=res["_id"], hide_title=("hide_title" in bottle.request.params))
    bottle.abort(404, bottle.template('Charity {{regno}} not found.', regno=regno))


@app.route('/orgid/<orgid>.json')
def orgid_json(orgid):
    """
    Fetch json representation based on a org-id for a record
    """
    query = {
        "query": {
            "match": {
                "org-ids": {
                    "query": orgid,
                    "operator": "and",
                }
            }
        }
    }
    res = app.config["es"].search(index=app.config["es_index"],
                                  doc_type=app.config["es_type"],
                                  body=query,
                                  _source_exclude=["complete_names"],
                                  ignore=[404])
    if res.get("hits", {}).get("hits", []):
        org = res["hits"]["hits"][0]["_source"]
        org.update({"id": res["hits"]["hits"][0]["_id"]})
        return org
    bottle.abort(404, bottle.template(
        'Orgid {{orgid}} not found.', orgid=orgid))

@app.route('/orgid/<orgid>')
@app.route('/orgid/<orgid>.html')
def orgid_html(orgid):
    """
    Redirect to a record based on the org-id
    """
    org = orgid_json(orgid)
    bottle.redirect('/charity/{}'.format(org["id"]))


@app.route('/feeds/ccew.<filetype>')
def ccew_rss(filetype):
    """
    Get an RSS feed based on when data is
    uploaded by the Charity Commission
    """
    ccew_url = 'http://data.charitycommission.gov.uk/'
    res = requests.get(ccew_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    items = []
    for i in soup.find_all('blockquote'):
        links = i.find_all('a')
        idate = parser.parse(
            i.h4.string.split(", ")[1],
            default=datetime(2018, 1, 12, 0, 0)
        ).replace(tzinfo=timezone.utc)
        items.append({
            "name": i.h4.string,
            "date": idate,
            "link": links[0].get('href'),
            "author": "Charity Commission for England and Wales",
        })

    feed_contents = dict(
        items=items,
        title='Charity Commission for England and Wales data downloads',
        description='Downloads available from Charity Commission data downloads page.',
        url=ccew_url,
        feed_url=bottle.request.url,
        updated=datetime.now().replace(tzinfo=timezone.utc),
    )

    if filetype == 'atom':
        bottle.response.content_type = 'application/atom+xml'
        template = 'atom.xml'
    elif filetype == "json":
        bottle.response.content_type = 'application/json'
        return {
            "version": "https://jsonfeed.org/version/1",
            "title": feed_contents["title"],
            "home_page_url": feed_contents["url"],
            "feed_url": feed_contents["feed_url"],
            "description": feed_contents["description"],
            "items": [
                {
                    "id": item["link"],
                    "url": item["link"],
                    "title": item["name"],
                    "date_published": item["date"].isoformat(),
                } for item in items
            ]
        }
    else:
        bottle.response.content_type = 'application/rss+xml'
        template = 'rss.xml'

    return bottle.template(template, **feed_contents)


@app.route('/about')
def about():
    """About page
    """
    return bottle.template('about', this_year=datetime.now().year)


@app.route('/autocomplete')
def autocomplete():
    search = bottle.request.params.q
    doc = {
        "suggest": {
            "suggest-1": {
                "prefix": search,
                "completion": {
                    "field": "complete_names",
                    "fuzzy" : {
                        "fuzziness" : 1
                    }
                }
            }
        }
    }
    res = app.config["es"].search(
        index=app.config["es_index"], doc_type="csv_data", body=doc,
        _source_include=['known_as'])
    return {"results": [
        {
            "label": x["_source"]["known_as"],
            "value": x["_id"]
        } for x in res.get("suggest", {}).get("suggest-1", [])[0]["options"]
    ]}


def get_csv_options():
    # work out CSV options
    csv_options = {}
    for o, v in app.config["csv_options"].items():
        values = [v for v in v[1]]
        csv_options[o] = values[0]
        if o in bottle.request.forms:
            if bottle.request.forms[o] in values:
                csv_options[o] = bottle.request.forms[o]

    if csv_options["escapechar"] == "":
        csv_options["escapechar"] = None
    csv_options["doublequote"] = csv_options["doublequote"] == 1

    return csv_options


@app.get('/adddata')
def uploadcsv():
    return bottle.template('csv_upload', error=None,
                           csv_max_rows=app.config["max_csv_rows"],
                           csv_options=app.config["csv_options"])

@app.post('/adddata')
def uploadcsv_post():
    upload = bottle.request.files.get('uploadcsv')

    if not upload:
        return bottle.template('csv_upload',
                               error="No file attached.",
                               csv_max_rows=app.config["max_csv_rows"],
                               csv_options=app.config["csv_options"])

    _, ext = os.path.splitext(upload.filename)
    if ext not in ('.csv', '.tsv', '.txt'):
        return bottle.template('csv_upload',
                               error="File extension \"{}\" not allowed".format(ext),
                               csv_max_rows=app.config["max_csv_rows"],
                               csv_options=app.config["csv_options"])

    # Select encoding and other CSV options

    # - store the CSV data somewhere (elasticsearch?)
    filedata = {
        "data": [],
        "name": upload.filename,
        "ext": ext,
        "fields": [],
        "reconcile_field": None,
        "uploaded": datetime.now(),
        "size": upload.content_length,
        "type": upload.content_type,
    }

    # work out CSV options
    csv_options = get_csv_options()

    filedata["file_encoding"] = csv_options["file_encoding"]
    del csv_options["file_encoding"]
    filedata["csvoptions"] = csv_options

    fileinput = io.TextIOWrapper(upload.file, encoding=filedata["file_encoding"])
    reader = csv.DictReader(fileinput, **filedata["csvoptions"])
    for k, r in enumerate(reader):
        # Limit on file size
        if k > app.config["max_csv_rows"]:
            return bottle.template('csv_upload',
                                   error="File too big (more than {} rows)".format(app.config["max_csv_rows"]),
                                   csv_max_rows=app.config["max_csv_rows"],
                                   csv_options=app.config["csv_options"])
        filedata["data"].append(r)
    filedata["fields"] = reader.fieldnames
    res = app.config["es"].index(index=app.config["es_index"], doc_type="csv_data", body=filedata)

    # - redirect to page with unique ID for dataset
    bottle.redirect('/adddata/{}'.format(res["_id"]))

@app.get('/adddata/<fileid>')
def uploadcsv_existing(fileid):
    # - select column you want to reconcile
    # - select any other columns you want to show
    # - present reconciliation choices
    # - download the resulting CSV file

    # allow option to delete file
    res = app.config["es"].get(index=app.config["es_index"], doc_type="csv_data", id=fileid)
    return bottle.template('csv_findfield', file=res["_source"], fileid=fileid)

@app.post('/adddata/<fileid>')
def uploadcsv_existing_post(fileid):
    res = app.config["es"].get(index=app.config["es_index"], doc_type="csv_data", id=fileid)
    reconcile_field = bottle.request.forms.get("reconcile_field", res["_source"]["reconcile_field"])
    charity_number_field = bottle.request.forms.get(
        "charity_number_field",
        res["_source"].get("charity_number_field","charity_number")
    )
    res["_source"]["reconcile_field"] = reconcile_field
    res["_source"]["charity_number_field"] = charity_number_field
    results = []

    to_reconcile = [r[reconcile_field] for r in res["_source"]["data"]]

    for r in to_reconcile:
        response = esdoc_orresponse(recon_query(r))
        response["query"] = r
        results.append(response)

    res["_source"]["reconcile_results"] = results

    res = app.config["es"].index(index=app.config["es_index"], doc_type="csv_data", id=res["_id"], body=res["_source"])
    bottle.redirect('/adddata/{}/reconcile'.format(res["_id"]))

@app.get('/adddata/<fileid>/reconcile')
def uploadcsv_results(fileid):
    # - select column you want to reconcile
    # - select any other columns you want to show
    # - present reconciliation choices
    # - download the resulting CSV file

    # allow option to delete file
    res = app.config["es"].get(index=app.config["es_index"], doc_type="csv_data", id=fileid)
    res["_source"]["reconcile_results"] = {
        r["query"]: r for r in res["_source"]["reconcile_results"]
    }

    return bottle.template('csv_checkreconciliation', file=res["_source"], fileid=fileid)

@app.post('/adddata/<fileid>/match')
def adddata_matched(fileid):
    # @TODO: add origin confirmation so that it can't be changed by itself.
    res = app.config["es"].get(index=app.config["es_index"], doc_type="csv_data", id=fileid)
    row = int(bottle.request.params.get("row"))
    match_id = bottle.request.params.get("match_id")
    field_name = res["_source"].get("charity_number_field", "charity_number")
    unmatch = "unmatch" in bottle.request.params
    if match_id == "":
        unmatch = True
    res["_source"]["charity_number_field"] = field_name

    for i, v in enumerate(res["_source"]["data"]):
        if i == row:
            v[field_name] = None if unmatch else match_id
        else:
            v[field_name] = None

    res = app.config["es"].index(
        index=app.config["es_index"], doc_type="csv_data", id=res["_id"], body=res["_source"])
    return res


@app.get('/adddata/<fileid>/reconcile.csv')
def uploadcsv_results_csv(fileid):
    # - download the resulting CSV file
    res = app.config["es"].get(index=app.config["es_index"], doc_type="csv_data", id=fileid)
    reconcile_field = res["_source"]["reconcile_field"]

    output = io.StringIO()
    csv_writer = csv.DictWriter(output, fieldnames=res["_source"]["fields"] + ["reconcile_result"])
    csv_writer.writeheader()
    for r in res["_source"]["data"]:
        r["reconcile_result"] = res["_source"]["reconcile_results"][r[reconcile_field]]["result"][0]["id"]
        csv_writer.writerow(r)

    bottle.response.set_header("Content-Type", "text/csv")
    return output.getvalue()

@app.get('/admin/uploaded-files')
@bottle.auth_basic(check_password)
def uploadcsv_see_files():
    doc = {'size' : 10000, 'query': {'match_all' : {}}, "sort": [{"uploaded": "desc"}]}
    res = app.config["es"].search(index=app.config["es_index"], doc_type="csv_data", body=doc)
    return bottle.template('uploaded_files', files=res["hits"]["hits"])


@app.route('/static/<filename:path>')
def send_static(filename):
    return bottle.static_file(filename, root='static')


def sort_out_date(charity_record):
    """
    parse date fields in a charity record
    """
    date_fields = ["date_registered", "date_removed", "last_modified"]
    for date_field in date_fields:
        if charity_record.get(date_field):
            try:
                charity_record[date_field] = parser.parse(
                    charity_record[date_field])
            except ValueError:
                pass
    return charity_record


def main():
    """
    Run the server (command line version)
    """

    parser_args = argparse.ArgumentParser(description='')  # @TODO fill in

    # server options
    parser_args.add_argument('-host', '--host', default="localhost", help='host for the server')
    parser_args.add_argument('-p', '--port', default=8080, help='port for the server')
    parser_args.add_argument('--debug', action='store_true', dest="debug", help='Debug mode (autoreloads the server)')
    parser_args.add_argument('--server', default="auto", help='Server backend to use (see http://bottlepy.org/docs/dev/deployment.html#switching-the-server-backend)')

    # http auth
    parser.add_argument('--admin-password', help='Password for accessing admin pages')

    # elasticsearch options
    parser_args.add_argument('--es-host', default="localhost", help='host for the elasticsearch instance')
    parser_args.add_argument('--es-port', default=9200, help='port for the elasticsearch instance')
    parser_args.add_argument('--es-url-prefix', default='', help='Elasticsearch url prefix')
    parser_args.add_argument('--es-use-ssl', action='store_true', help='Use ssl to connect to elasticsearch')
    parser_args.add_argument('--es-index', default='charitysearch', help='index used to store charity data')
    parser_args.add_argument('--es-type', default='charity', help='type used to store charity data')

    parser_args.add_argument('--ga-tracking-id', help='Google Analytics Tracking ID')

    args = parser_args.parse_args()

    app.config["es"] = Elasticsearch(
        host=args.es_host,
        port=args.es_port,
        url_prefix=args.es_url_prefix,
        use_ssl=args.es_use_ssl
    )
    app.config["es_index"] = args.es_index
    app.config["es_type"] = args.es_type
    app.config["ga_tracking_id"] = args.ga_tracking_id
    app.config["max_csv_rows"] = 1000
    app.config["admin_password"] = args.admin_password

    bottle.debug(args.debug)

    bottle.run(app, server=args.server, host=args.host, port=args.port, reloader=args.debug)

if __name__ == '__main__':
    main()
