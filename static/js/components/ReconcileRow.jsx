import React from "react";
import { connect } from "react-redux";
import ReconcileResultList from "./ReconcileResultList"

const mapStateToProps = (state, ownProps) => {
    let fields = state.fields.filter((field) => {
        return (!state.hidden_fields.includes(field) ||
            field == state.reconcile_field);
    });
    return { 
        fields: fields,
        data: ownProps.data,
        reconcile_field: state.reconcile_field,
        reconcile_result: ownProps.reconcile_result,
        rowid: ownProps.rowid
    };
};

class ReconcileRow extends React.Component {

    render() {
        return (
            <tr>
                {
                    this.props.fields.map((field, i) =>
                        <React.Fragment key={i}>
                            <td>{this.props.data[field]}</td>
                            {this.props.reconcile_field == field &&
                                <td>
                                    <ReconcileResultList matches={this.props.reconcile_result} rowid={this.props.rowid} />
                                </td>}
                        </React.Fragment>
                    )
                }
            </tr>
        )
    }
}

export default connect(mapStateToProps)(ReconcileRow);