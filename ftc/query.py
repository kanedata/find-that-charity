
def random_query(active=False, orgtype=None, aggregate=False, source=None):
    query = {
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must": []
                    }
                },
                "boost": "5",
                "random_score": {},
                "boost_mode": "multiply"
            }
        }
    }
    if active:
        query["query"]["function_score"]["query"]["bool"]["must"].append({
            "match": {
                "active": True
            }
        })

    if orgtype and orgtype != ['']:
        if not isinstance(orgtype, list):
            orgtype = [orgtype]
        query["query"]["function_score"]["query"]["bool"]["must"].append({
            "terms": {
                "organisationType": orgtype
            }
        })

    if source and source != ['']:
        if not isinstance(source, list):
            source = [source]
        query["query"]["function_score"]["query"]["bool"]["must"].append({
            "terms": {
                "sources": source
            }
        })

    if aggregate:
        query["aggs"] = {
            "group_by_type": {
                "terms": {
                    "field": "organisationType",
                    "size": 500
                }
            },
            "group_by_source": {
                "terms": {
                    "field": "sources",
                    "size": 500
                }
            }
        }

    return query
