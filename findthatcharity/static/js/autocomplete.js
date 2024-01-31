const createEl = (tag, { classList, id } = {}) => {
    let el = document.createElement(tag);
    if (typeof classList === 'string') {
        classList = classList.split(' ');
    }
    if (Array.isArray(classList)) {
        el.classList.add(...classList);
    }
    if (typeof id === 'string') {
        el.id = id;
    }
    return el;
}

// Credit David Walsh (https://davidwalsh.name/javascript-debounce-function)

// Returns a function, that, as long as it continues to be invoked, will not
// be triggered. The function will be called after it stops being called for
// N milliseconds. If `immediate` is passed, trigger the function on the
// leading edge, instead of the trailing.
function debounce(func, wait, immediate) {
    var timeout;

    return function executedFunction() {
        var context = this;
        var args = arguments;

        var later = function () {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };

        var callNow = immediate && !timeout;

        clearTimeout(timeout);

        timeout = setTimeout(later, wait);

        if (callNow) func.apply(context, args);
    };
};

const getHighlightedText = (text, highlight) => {
    // Split text on higlight term, include term itself into parts, ignore case
    // https://stackoverflow.com/questions/29652862/highlight-text-using-reactjs
    highlight = highlight.trim();
    var parts = text.split(new RegExp(`(${highlight})`, 'gi'));
    let span = createEl('span', { classList: 'mr2 dib' });
    parts.forEach((part) => {
        if (part.toLowerCase() === highlight.toLowerCase()) {
            let highlight = createEl('span', { classList: ['bg-yellow', 'i'] });
            highlight.innerText = part;
            span.append(highlight);
        } else {
            span.append(part);
        }
    });
    return span;
}

const updateAutoComplete = (results, el, q) => {
    el.innerHTML = '';
    if (results.length == 0) {
        el.classList.add('dn');
        return;
    }
    let ul = createEl('ul', { classList: 'list pa0 ma0 f6 br2 b--light-gray bw1 ba' });
    results.forEach((r) => {
        let li = createEl('li', { classList: 'pa3 bb b--light-gray' });
        let a = createEl('a', {
            classList: 'link dark-blue underline-hover pointer',
        });
        a.setAttribute('href', ORG_ID_URL.replace("__id__", r.id));
        a.append(
            getHighlightedText(r.name, q)
        );
        if (r.notable) {
            let orgtype = createEl('span', { classList: 'fr gray i ml1 dib' });
            orgtype.innerText = ORGTYPES[r.notable[0]];
            a.append(orgtype);
        }
        li.append(a);
        ul.append(li);
    });
    el.append(ul);
    el.classList.remove('dn');
}

var latestTargetValue = null;
const fetchAutocomplete = () => {
    const resultsContainer = document.getElementById('autocomplete-results');
    const q = document.getElementById('search-autocomplete-q');
    const orgtype = document.getElementById('search-autocomplete-orgtype').value;
    let v = q.value;
    latestTargetValue = v;
    if (v.length <= 3) {
        updateAutoComplete([], resultsContainer, v);
        return;
    }
    var url = new URL(AUTOCOMPLETE_URL);
    if (orgtype) {
        var url = new URL(AUTOCOMPLETE_ORGTYPE_URL.replace("__orgtype__", orgtype));
    }
    url.searchParams.append('prefix', v);
    fetch(url)
        .then((r) => {
            var url = new URL(r.url);
            if (url.searchParams.get('prefix') == latestTargetValue) {
                return r.json();
            }
            throw new Error("Not searching for latest value");
        })
        .then((r) => {
            updateAutoComplete(
                r["result"],
                resultsContainer,
                v
            );
        })
        .catch((err) => {
            if (err.message !== "Not searching for latest value") {
                throw err;
            }
        });
}

document.getElementById('search-autocomplete-q').addEventListener('keyup', debounce((e) => {
    e.preventDefault();
    fetchAutocomplete();
}, 300));
document.getElementById('search-autocomplete-orgtype').addEventListener('change', (e) => {
    e.preventDefault();
    fetchAutocomplete();
});