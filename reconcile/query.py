from charity.models import (
    CCEWCharityAreaOfOperation,
    CCEWCharityARPartA,
    CCEWCharityARPartB,
    CCEWCharityGoverningDocument,
)
from findthatcharity.jinja2 import get_orgtypes
from findthatcharity.utils import normalise_name, to_titlecase
from ftc.query import OrganisationSearch
from ftc.models import Organisation
from ftc.models.organisation_classification import OrganisationClassification


def do_reconcile_query(
    query,
    orgtypes="all",
    type="/Organization",
    limit=5,
    properties=[],
    type_strict="should",
):
    if not query:
        return []

    if not isinstance(orgtypes, list) and orgtypes != "all":
        orgtypes = orgtypes.split("+")

    properties = {p["pid"]: p["v"] for p in properties}

    s = OrganisationSearch(
        other_orgtypes=orgtypes,
        term=query,
        postcode=properties.get("postalCode"),
        domain=properties.get("domain"),
    )
    s.run_db()
    all_orgtypes = get_orgtypes()
    result = sorted(list(o for o in s.query), key=lambda o: o.rank, reverse=True)

    return {
        "result": [
            {
                "id": o.org_id,
                "name": "{} ({}){}".format(
                    to_titlecase(o.name),
                    o.org_id,
                    "" if o.active else " [INACTIVE]",
                ),
                "type": [
                    {
                        "id": o.organisationTypePrimary.slug,
                        "name": o.organisationTypePrimary.title,
                    }
                ]
                + [
                    {"id": ot, "name": all_orgtypes[ot].title}
                    for ot in o.organisationType
                    if ot != o.organisationTypePrimary.slug and ot in all_orgtypes
                ],
                "score": o.rank,
                "match": (normalise_name(o.name) == normalise_name(query)) and (k == 0),
            }
            for k, o in enumerate(result)
        ]
    }


def do_extend_query(ids, properties):
    result = {"meta": [], "rows": {}}
    all_fields = [p["id"] for p in properties]

    # get organisation data
    all_organisation_fields = {
        f["id"]: f for f in Organisation.get_fields_as_properties()
    }
    organisation_fields = [
        p["id"] for p in properties if p["id"] in all_organisation_fields.keys()
    ]
    result["meta"] = [all_organisation_fields[f] for f in organisation_fields]
    for r in Organisation.objects.filter(org_id__in=ids).values(
        "org_id", *organisation_fields
    ):
        result["rows"][r["org_id"]] = {
            k: v for k, v in r.items() if k in organisation_fields
        }

    # get vocabulary data
    vocab_fields = [
        f.replace("vocab-", "") for f in all_fields if f.startswith("vocab-")
    ]
    for entry in OrganisationClassification.objects.filter(
        org_id__in=ids, vocabulary__vocabulary__slug__in=vocab_fields
    ).all():
        vocab_slug = entry.vocabulary.vocabulary.slug
        if entry.org_id not in result["rows"]:
            result["rows"][entry.org_id] = {}
        if "vocab-" + vocab_slug not in result["rows"][entry.org_id]:
            result["rows"][entry.org_id]["vocab-" + vocab_slug] = []
        result["rows"][entry.org_id]["vocab-" + vocab_slug].append(
            entry.vocabulary.title
        )

    # get charity data
    ccew_fields = {}
    for f in all_fields:
        if f.startswith("ccew-"):
            table, field_name = f.replace("ccew-", "").split("-", 1)
            ccew_fields.setdefault(table, []).append(field_name)
    ccew_ids = [i.replace("GB-CHC-", "") for i in ids if i.startswith("GB-CHC-")]

    tables = (
        ("parta", CCEWCharityARPartA, {"latest_fin_period_submitted_ind": True}),
        ("partb", CCEWCharityARPartB, {"latest_fin_period_submitted_ind": True}),
        ("gd", CCEWCharityGoverningDocument, {"linked_charity_number": 0}),
        ("aoo", CCEWCharityAreaOfOperation, {"linked_charity_number": 0}),
    )

    for table, model, default_filters in tables:
        if ccew_fields.get(table):
            for r in model.objects.filter(
                registered_charity_number__in=ccew_ids,
                **default_filters,
            ).values("registered_charity_number", *ccew_fields[table]):
                org_id = "GB-CHC-" + str(r["registered_charity_number"])
                if org_id not in result["rows"]:
                    result["rows"][org_id] = {}
                for f in ccew_fields[table]:
                    fieldname = f"ccew-{table}-{f}"
                    if result["rows"][org_id].get(fieldname):
                        if not isinstance(result["rows"][org_id][fieldname], list):
                            result["rows"][org_id][fieldname] = [
                                result["rows"][org_id][fieldname]
                            ]
                        result["rows"][org_id][fieldname].append(r.get(f))
                    else:
                        result["rows"][org_id][fieldname] = r.get(f)

    # add in rows for any data that is missing
    for i in ids:
        if i not in result["rows"]:
            result["rows"][i] = {k: None for k in all_fields}

    return result


def autocomplete_query(term, orgtype="all"):
    """
    Look up an organisation using the first part of the name
    """
    doc = {
        "suggest": {
            "suggest-1": {
                "prefix": term,
                "completion": {"field": "complete_names", "fuzzy": {"fuzziness": 1}},
            }
        }
    }

    # if not orgtype or orgtype == 'all':
    #     orgtype = [o.slug for o in OrganisationType.objects.all()]
    # elif orgtype:
    #     orgtype = orgtype.split("+")

    # doc["suggest"]["suggest-1"]["completion"]["contexts"] = {
    #     "organisationType": orgtype
    # }

    return doc
