import React from "react";
import { connect } from "react-redux";

import ReconcileStage from "./Stage"
import ReconcileForm from "./Upload/Form"
import ReconcileSummary from "./ReconcileSummary"
import ReconcileTable from "./ReconcileTable"
import ReconcileFieldFilter from "./ReconcileFieldFilter"
import ReconcileAddData from "./AddData/Form"

const mapStateToProps = (state) => {
    return {
        stage: state.stage
    };
};

class ReconcileApp extends React.Component {
    render() {
        switch(this.props.stage){
            // find a field in the data with a charity name in it
            case 'namefield':
                return (
                    <React.Fragment>
                        <ReconcileStage stage={this.props.stage} />
                    </React.Fragment>
                )

            // reconcile the results
            case 'reconcile':
                return (
                    <React.Fragment>
                        <ReconcileStage stage={this.props.stage} />
                        <ReconcileSummary />
                        <ReconcileFieldFilter />
                        <ReconcileTable />
                    </React.Fragment>
                )

            // add charity data to the field
            case 'adddata':
                return (
                    <React.Fragment>
                        <ReconcileStage stage={this.props.stage} />
                        <ReconcileAddData />
                    </React.Fragment>
                )

            // download the resulting data
            case 'download':
                return (
                    <React.Fragment>
                        <ReconcileStage stage={this.props.stage} />
                    </React.Fragment>
                )

            // Upload a file
            case 'upload':  
            default:
                return (
                    <React.Fragment>
                        <ReconcileStage stage={this.props.stage} />
                        <ReconcileForm />
                    </React.Fragment>
                )
        }
    }
}

export default connect(mapStateToProps)(ReconcileApp);