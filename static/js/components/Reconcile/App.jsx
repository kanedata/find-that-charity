import React from "react";
import { connect } from "react-redux";

import ReconcileStage from "./Stage"
import ReconcileForm from "./Upload/Form"
import ReconcileAddData from "./AddData/Form"
import ReconcileDownloadData from "./Download/Link"

const mapStateToProps = (state) => {
    return {
        stage: state.stage
    };
};

class ReconcileApp extends React.Component {
    render() {
        switch(this.props.stage){

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
                        <ReconcileDownloadData />
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