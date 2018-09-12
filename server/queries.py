"""
Useful functions for creating queries
"""
import json
import yaml

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


def esdoc_orresponse(query, app):
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


def service_spec(app, service_url):
    """Return the default service specification

    Specification found here: https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation-Service-API#service-metadata
    """
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
