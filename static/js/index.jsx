import React from "react";
import ReactDOM from "react-dom";
import SearchAutoComplete from "./SearchAutoComplete";
import ReconcileResultList from "./ReconcileResultList";

require('../../node_modules/bulma/css/bulma.css');
require('../../node_modules/font-awesome/css/font-awesome.min.css');
require('../../node_modules/bulma-steps/dist/bulma-steps.min.css');
require('../../node_modules/bulma-quickview/dist/bulma-quickview.min.css');

const search_form = document.querySelector('#search-autocomplete')
if(search_form){
    ReactDOM.render(
        <SearchAutoComplete value={search_form.q.value} />,
        search_form.querySelector(".field")
    );
}

document.querySelectorAll('.reconcile-result').forEach(function (recon_result) {
    var result = JSON.parse(decodeURI(recon_result.dataset.results));
    ReactDOM.render(
        <ReconcileResultList matches={result} />,
        recon_result
    );
});