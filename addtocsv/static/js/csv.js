const DEFAULT_HASH_LENGTH = 4;
const ARRAY_CHUNK_SIZE = 100;
const FIELD_MATCH_REGEX = /(organi[sz]ation|org_?id)/g;

function chunk_array(arr, len) {
    var chunks = [],
        i = 0,
        n = arr.length;
    while (i < n) {
        chunks.push(arr.slice(i, i += len));
    }
    return chunks;
}


function openSaveFileDialog(data, filename, mimetype) {
    // from: https://github.com/mholt/PapaParse/issues/175#issuecomment-395978144

    if (!data) return;

    var blob = data.constructor !== Blob
        ? new Blob([data], { type: mimetype || 'application/octet-stream' })
        : data;

    if (navigator.msSaveBlob) {
        navigator.msSaveBlob(blob, filename);
        return;
    }

    var lnk = document.createElement('a'),
        url = window.URL,
        objectURL;

    if (mimetype) {
        lnk.type = mimetype;
    }

    lnk.download = filename || 'untitled';
    lnk.href = objectURL = url.createObjectURL(blob);
    lnk.dispatchEvent(new MouseEvent('click'));
    setTimeout(url.revokeObjectURL.bind(url, objectURL));

}

function extractProperties(orgRecord) {
    // properties are stored as a list of dicts, with a single key/value pair
    // // We don't neeed to extract the key, so we just return the value
    return Object.fromEntries(Object.entries(orgRecord).map(
        ([k, v]) => [k, Object.values(v).map((v) => Object.values(v)).join("; ")]
    ));
}

var app = new Vue({
    el: '#addtocsv',
    data: {
        fields: [],
        csv: null,
        csv_results: null,
        field_select: [],
        fields_to_add: [
            "org_id",
            "name",
            // "postalCode",
            "url",
            "latestIncome",
            "latestIncomeDate",
            "dateRegistered",
            "dateRemoved",
            "active",
            "source",
        ],
        column_to_use: null,
        column_to_use_auto: false,
        identifier_type: null,
        identifier_types: ORGID_SCHEMES,
        progress: null,
    },
    delimiters: ['[[', ']]'],
    mounted() {
        fetch(PROPERTIES_URL)
            .then(r => r.json())
            .then(r => (this.fields = r.properties))
    },
    methods: {
        resetFile: function () {
            this.csv = null;
            this.csv_results = null;
            this.field_select = [];
            this.fields_to_add = [];
            this.column_to_use = null;
            this.column_to_use_auto = false;
            this.progress = null;
        },
        selectFile: function (ev) {
            this.csv = ev.target.files[0];
            var component = this;

            Papa.parse(this.csv, {
                header: true,
                worker: true,
                complete: function (results) {
                    component.csv_results = results;
                    component.field_select = results.meta.fields.map((f) => ({
                        name: f,
                        slug: f.toLowerCase().replace(/"\s+"/gi, "-").replace(/[^a-z0-9]/gi, ''),
                        example_values: results.data
                            .map((d) => d[f])
                            .filter((v, i, a) => a.indexOf(v) === i)
                            .slice(0, 5)
                    }));
                    could_use = component.field_select.filter((f) => FIELD_MATCH_REGEX.test(f.name));
                    if (could_use.length > 0) {
                        component.column_to_use = could_use[0].name;
                        component.column_to_use_auto = true;
                    }
                }
            });
        },
        getRowIdentifier: function (row) {
            var id = row[this.column_to_use];
            if (!id) return null;
            if (this.identifier_type == 'orgid') {
                return id;
            }
            if (this.identifier_type == 'charity') {
                if (id.startsWith("S")) {
                    return `GB-SC-${id}`;
                } else if (id.startsWith("N")) {
                    return `GB-NIC-${id.replace("[NI]+", "")}`;
                }
                return `GB-CHC-${id}`;
            }
            return `${this.identifier_type}-${id}`;
        },
        selectAllFields: function () {
            if (this.fields_to_add.length) {
                this.fields_to_add = [];
            } else {
                this.fields_to_add = this.fields.map((f) => f.id);
            }
        },
        getResults: function () {
            var component = this;
            var ids = this.csv_results.data.map((d) => component.getRowIdentifier(d)).filter((id) => id);
            var id_chunks = chunk_array(ids, ARRAY_CHUNK_SIZE);
            var rows_done = 0;
            component.progress = 0;
            return Promise.all(id_chunks.map(id_chunk => {
                var body = new FormData();
                body.append("extend", JSON.stringify({
                    "ids": id_chunk,
                    "properties": component.fields_to_add.map((p) => ({ id: p })),
                }));
                return fetch(EXTEND_URL, {
                    method: 'POST',
                    body: body,
                })
                    .then((res) => {
                        rows_done += id_chunk.length;
                        component.progress = ((rows_done / ids.length) * 100).toFixed(1);
                        return res.json()
                    })
                    .then((data) => data.rows)
                    .catch((error) => {
                        console.log('Error: ', error)
                    })
            }))
                .then(data => Object.assign({}, ...data))
                .then(data => Object.fromEntries(Object.entries(data).map(
                    ([orgid, properties]) => (
                        [orgid, extractProperties(properties)]
                    )
                )))
                .then(new_data => openSaveFileDialog(
                    Papa.unparse({
                        fields: component.csv_results.meta.fields.concat(component.fields_to_add),
                        data: component.csv_results.data.map(row => Object.assign(
                            row,
                            new_data[component.getRowIdentifier(row)]
                        ))
                    }),
                    component.csv.name.replace(".csv", "-org.csv")
                ));
        },
    },
    computed: {
        stage: function () {
            if (!this.csv) {
                return 0;
            }
            if (this.identifier_type) {
                return 3;
            }
            if (this.column_to_use) {
                return 2;
            }
            return 1;
        },
        filename: function () {
            if (!this.csv) {
                return null;
            }
            if (this.csv_results) {
                return this.csv.name + " (" + this.csv_results.data.length + " rows)";
            }
            return this.csv.name;
        }
    }
})