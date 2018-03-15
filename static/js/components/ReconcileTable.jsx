import React from "react";
import { connect } from "react-redux";

import ReconcileHeaderRow from "./ReconcileHeaderRow"
import ReconcileRow from "./ReconcileRow"

const mapStateToProps = (state) => {
    return { 
        data: state.data,
        reconcile_field: state.reconcile_field,
        reconcile_results: state.reconcile_results
    };
};

class ReconcileTable extends React.Component {
    constructor(props) {
        super(props);
        this.getReconcileResult = this.getReconcileResult.bind(this);
    }

    getReconcileResult(datarow){
        var reconValue = datarow[this.props.reconcile_field];
        return this.props.reconcile_results[reconValue].result;
    }

    render() {
        return (
            <table className="table is-striped is-narrow">
                <thead>
                    <ReconcileHeaderRow fields={this.props.fields}  
                                        reconcile_field={this.props.reconcile_field} />
                </thead>
                <tbody>
                    {this.props.data.map((datarow, i) =>
                        <ReconcileRow key={i} 
                                      rowid={i}
                                      fields={this.props.fields} 
                                      data={datarow} 
                                      reconcile_field={this.props.reconcile_field}
                                      reconcile_result={this.getReconcileResult(datarow)} />
                    )}
                </tbody>
            </table>
        )
    }
}

export default connect(mapStateToProps)(ReconcileTable);