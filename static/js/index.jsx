import React from "react";
import ReactDOM from "react-dom";
import { createStore } from "redux";
import { Provider } from "react-redux";

import AutoCompleteSearch from "./components/AutoComplete/Search";
import ReconcileApp from "./components/Reconcile/App";
import rootReducer from "./reducers/Reducer";

require('../../node_modules/bulma/css/bulma.css');
require('../../node_modules/font-awesome/css/font-awesome.min.css');
require('../../node_modules/bulma-steps/dist/bulma-steps.min.css');
require('../../node_modules/bulma-quickview/dist/bulma-quickview.min.css');
require('../css/styles.css');

const search_form = document.querySelector('#search-autocomplete')
if(search_form){
    ReactDOM.render(
        <AutoCompleteSearch value={search_form.q.value} />,
        search_form.querySelector(".field")
    );
}

const reconcile_app = document.querySelector("#reconcile-root");
if(reconcile_app){
    var store = createStore(rootReducer);
    ReactDOM.render(
        <Provider store={store}>
            <ReconcileApp />
        </Provider>,
        reconcile_app
    )
}
