from __future__ import print_function
import os
import argparse
import bottle
import json
import yaml
from elasticsearch import Elasticsearch
from collections import OrderedDict
import time
import datetime
from dateutil import parser
import csv
import io

app = bottle.default_app()

# everywhere gives a different env var for elasticsearch services...
potential_env_vars = [
    "ELASTICSEARCH_URL",
    "ES_URL",
    "BONSAI_URL"
]
for e_v in potential_env_vars:
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
    with open('./es_config.yml', 'rb') as yaml_file:
        json_q = yaml.load(yaml_file)
        for p in json_q["params"]:
            json_q["params"][p] = term
        return json.dumps(json_q)


def recon_query(term):
    with open('./recon_config.yml', 'rb') as yaml_file:
        json_q = yaml.load(yaml_file)
        for p in json_q["params"]:
            json_q["params"][p] = term
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
    res = app.config["es"].search_template(index=app.config["es_index"], doc_type=app.config["es_type"], body=query, ignore=[404])
    res = res["hits"]
    for result in res["hits"]:
        result["_link"] = "/charity/" + result["_id"]
        result["_source"] = sort_out_date(result["_source"])
    return bottle.template('search', res=res, term=json.loads(query)["params"]["name"])


def check_password(usr, passwd):
    if passwd == app.config["admin_password"]:
        return True


@app.route('/')
def home():
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
        if filetype=="html":
            bottle.redirect("/charity/{}".format(char["_id"]))
        else:
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
            q = "q" + str(counter)
            # print(queries_json[q], queries_json[q]["query"])
            result = esdoc_orresponse(recon_query(queries_json[q]["query"]))["result"]
            results.update({q: {"result": result}})
            counter += 1
        return results

    # otherwise just return the service specification
    return service_spec()


@app.route('/charity/<regno>')
@app.route('/charity/<regno>.<filetype>')
def charity(regno, filetype='html'):
    res = app.config["es"].get(index=app.config["es_index"], doc_type=app.config["es_type"], id=regno, ignore=[404])
    if "_source" in res:
        if filetype == "html":
            return bottle.template('charity', charity=sort_out_date(res["_source"]), charity_id=res["_id"])
        else:
            return res["_source"]
    else:
        bottle.abort(404, bottle.template('Charity {{regno}} not found.', regno=regno))


@app.route('/preview/charity/<regno>')
@app.route('/preview/charity/<regno>.html')
def charity_preview(regno):
    res = app.config["es"].get(index=app.config["es_index"], doc_type=app.config["es_type"], id=regno, ignore=[404])
    if "_source" in res:
        return bottle.template('preview', charity=sort_out_date(res["_source"]), charity_id=res["_id"], hide_title=("hide_title" in bottle.request.params))
    else:
        bottle.abort(404, bottle.template('Charity {{regno}} not found.', regno=regno))


@app.route('/about')
def about():
    return bottle.template('about', this_year=datetime.datetime.now().year)


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
    upload     = bottle.request.files.get('uploadcsv')

    if not upload:
        return bottle.template('csv_upload', error="No file attached.", 
                            csv_max_rows=app.config["max_csv_rows"], 
                            csv_options=app.config["csv_options"])

    name, ext = os.path.splitext(upload.filename)
    if ext not in ('.csv', '.tsv', '.txt'):
        return bottle.template('csv_upload', error="File extension \"{}\" not allowed".format(ext), 
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
        "uploaded": datetime.datetime.now(),
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
            return bottle.template('csv_upload', error="File too big (more than {} rows)".format(app.config["max_csv_rows"]), 
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
    charity_number_field = bottle.request.forms.get("charity_number_field", res["_source"].get("charity_number_field","charity_number"))
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


def sort_out_date(charity):
    dates = ["date_registered", "date_removed", "last_modified"]
    for d in dates:
        if d in charity and charity[d]:
            try:
                charity[d] = parser.parse(charity[d])
            except ValueError:
                pass
    return charity


def main():

    parser = argparse.ArgumentParser(description='')  # @TODO fill in

    # server options
    parser.add_argument('-host', '--host', default="localhost", help='host for the server')
    parser.add_argument('-p', '--port', default=8080, help='port for the server')
    parser.add_argument('--debug', action='store_true', dest="debug", help='Debug mode (autoreloads the server)')
    parser.add_argument('--server', default="auto", help='Server backend to use (see http://bottlepy.org/docs/dev/deployment.html#switching-the-server-backend)')

    # http auth
    parser.add_argument('--admin-password', help='Password for accessing admin pages')

    # elasticsearch options
    parser.add_argument('--es-host', default="localhost", help='host for the elasticsearch instance')
    parser.add_argument('--es-port', default=9200, help='port for the elasticsearch instance')
    parser.add_argument('--es-url-prefix', default='', help='Elasticsearch url prefix')
    parser.add_argument('--es-use-ssl', action='store_true', help='Use ssl to connect to elasticsearch')
    parser.add_argument('--es-index', default='charitysearch', help='index used to store charity data')
    parser.add_argument('--es-type', default='charity', help='type used to store charity data')

    parser.add_argument('--ga-tracking-id', help='Google Analytics Tracking ID')

    args = parser.parse_args()

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
