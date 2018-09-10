import os
from datetime import datetime
import io
import csv

import bottle

from queries import esdoc_orresponse, recon_query

csv_app = bottle.Bottle()

csv_app.config["csv_options"] = {
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
csv_app.config["max_csv_rows"] = 1000


def check_password(_, passwd):
    """
    Check the admin password
    """
    if passwd == csv_app.config["admin_password"]:
        return True


def get_csv_options():
    """work out CSV options

    Based on the CSV options that come with python csv module
    """
    csv_options = {}
    for o, v in csv_app.config["csv_options"].items():
        values = [v for v in v[1]]
        csv_options[o] = values[0]
        if o in bottle.request.forms:
            if bottle.request.forms[o] in values:
                csv_options[o] = bottle.request.forms[o]

    if csv_options["escapechar"] == "":
        csv_options["escapechar"] = None
    csv_options["doublequote"] = csv_options["doublequote"] == 1

    return csv_options


@csv_app.get('/adddata')
def uploadcsv():
    """
    Form for uploading CSV
    """
    return bottle.template('csv_upload', error=None,
                           csv_max_rows=csv_app.config["max_csv_rows"],
                           csv_options=csv_app.config["csv_options"])


@csv_app.post('/adddata')
def uploadcsv_post():
    """
    Stage 2 of csv upload
    
    Checks file and then redirects to /adddata/<fileid> if successful
    Otherwise shows errors on upload page
    """
    upload = bottle.request.files.get('uploadcsv')

    if not upload:
        return bottle.template('csv_upload',
                               error="No file attached.",
                               csv_max_rows=csv_app.config["max_csv_rows"],
                               csv_options=csv_app.config["csv_options"])

    _, ext = os.path.splitext(upload.filename)
    if ext not in ('.csv', '.tsv', '.txt'):
        return bottle.template('csv_upload',
                               error="File extension \"{}\" not allowed".format(
                                   ext),
                               csv_max_rows=csv_app.config["max_csv_rows"],
                               csv_options=csv_app.config["csv_options"])

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

    fileinput = io.TextIOWrapper(
        upload.file, encoding=filedata["file_encoding"])
    reader = csv.DictReader(fileinput, **filedata["csvoptions"])
    for k, r in enumerate(reader):
        # Limit on file size
        if k > csv_app.config["max_csv_rows"]:
            return bottle.template('csv_upload',
                                   error="File too big (more than {} rows)".format(
                                       csv_app.config["max_csv_rows"]),
                                   csv_max_rows=csv_app.config["max_csv_rows"],
                                   csv_options=csv_app.config["csv_options"])
        filedata["data"].append(r)
    filedata["fields"] = reader.fieldnames
    res = csv_app.config["es"].index(
        index=csv_app.config["es_index"], doc_type="csv_data", body=filedata)

    # - redirect to page with unique ID for dataset
    bottle.redirect('/adddata/{}'.format(res["_id"]))


@csv_app.get('/adddata/<fileid>')
def uploadcsv_existing(fileid):
    """
    Stage 2 of CSV upload - select the field that contains the name to reconcile

    TODO:
    # - select column you want to reconcile
    # - select any other columns you want to show
    # - present reconciliation choices
    # - download the resulting CSV file

    # allow option to delete file
    """
    res = csv_app.config["es"].get(
        index=csv_app.config["es_index"], doc_type="csv_data", id=fileid)
    return bottle.template('csv_findfield', file=res["_source"], fileid=fileid)


@csv_app.post('/adddata/<fileid>')
def uploadcsv_existing_post(fileid):
    """
    Post request for stage 2 of csv upload

    Reconciles data using the fields given
    """
    res = csv_app.config["es"].get(
        index=csv_app.config["es_index"], doc_type="csv_data", id=fileid)
    reconcile_field = bottle.request.forms.get(
        "reconcile_field", res["_source"]["reconcile_field"])
    charity_number_field = bottle.request.forms.get(
        "charity_number_field",
        res["_source"].get("charity_number_field", "charity_number")
    )
    res["_source"]["reconcile_field"] = reconcile_field
    res["_source"]["charity_number_field"] = charity_number_field
    results = []

    to_reconcile = [r[reconcile_field] for r in res["_source"]["data"]]

    for r in to_reconcile:
        response = esdoc_orresponse(recon_query(r), csv_app)
        response["query"] = r
        results.append(response)

    res["_source"]["reconcile_results"] = results

    res = csv_app.config["es"].index(
        index=csv_app.config["es_index"], doc_type="csv_data", id=res["_id"], body=res["_source"])
    bottle.redirect('/adddata/{}/reconcile'.format(res["_id"]))


@csv_app.get('/adddata/<fileid>/reconcile')
def uploadcsv_results(fileid):
    """
    Get the results of the reconciliation and display to user to verify
    """
    # - select column you want to reconcile
    # - select any other columns you want to show
    # - present reconciliation choices
    # - download the resulting CSV file

    # allow option to delete file
    res = csv_app.config["es"].get(
        index=csv_app.config["es_index"], doc_type="csv_data", id=fileid)
    res["_source"]["reconcile_results"] = {
        r["query"]: r for r in res["_source"]["reconcile_results"]
    }

    return bottle.template('csv_checkreconciliation', file=res["_source"], fileid=fileid)


@csv_app.post('/adddata/<fileid>/match')
def adddata_matched(fileid):
    """
    Small API for updating an individual match
    """
    # @TODO: add origin confirmation so that it can't be changed by itself.
    res = csv_app.config["es"].get(
        index=csv_app.config["es_index"], doc_type="csv_data", id=fileid)
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

    res = csv_app.config["es"].index(
        index=csv_app.config["es_index"], doc_type="csv_data", id=res["_id"], body=res["_source"])
    return res


@csv_app.get('/adddata/<fileid>/reconcile.csv')
def uploadcsv_results_csv(fileid):
    """
    Download the resulting CSV file
    """
    res = csv_app.config["es"].get(
        index=csv_app.config["es_index"], doc_type="csv_data", id=fileid)
    reconcile_field = res["_source"]["reconcile_field"]

    output = io.StringIO()
    csv_writer = csv.DictWriter(
        output, fieldnames=res["_source"]["fields"] + ["reconcile_result"])
    csv_writer.writeheader()
    for r in res["_source"]["data"]:
        r["reconcile_result"] = res["_source"]["reconcile_results"][r[reconcile_field]
                                                                   ]["result"][0]["id"]
        csv_writer.writerow(r)

    bottle.response.set_header("Content-Type", "text/csv")
    return output.getvalue()


@csv_app.get('/admin/uploaded-files')
@bottle.auth_basic(check_password)
def uploadcsv_see_files():
    """
    Basic admin interface for checking the uploaded files
    """
    doc = {'size': 10000, 'query': {'match_all': {}},
           "sort": [{"uploaded": "desc"}]}
    res = csv_app.config["es"].search(
        index=csv_app.config["es_index"], doc_type="csv_data", body=doc)
    return bottle.template('uploaded_files', files=res["hits"]["hits"])
