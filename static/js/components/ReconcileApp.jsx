import React from "react";
import ReconcileSummary from "./ReconcileSummary"
import ReconcileTable from "./ReconcileTable"
import ReconcileFieldFilter from "./ReconcileFieldFilter"

export default class ReconcileApp extends React.Component {
    render() {
        return (
            <React.Fragment>
                <ReconcileSummary />
                <ReconcileFieldFilter />
                <ReconcileTable />
            </React.Fragment>
        )
    }
}
