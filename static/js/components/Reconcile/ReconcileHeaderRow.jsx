import React from "react";
import { connect } from "react-redux";

const mapStateToProps = (state) => {
    let fields = state.fields.filter((field) => {
        return (!state.hidden_fields.includes(field) ||
            field == state.reconcile_field);
    });
    return {
        fields: fields,
        reconcile_field: state.reconcile_field
    };
};

class ReconcileHeaderRow extends React.Component {
    render() {
        return (
            <tr>
                {
                    this.props.fields.map((field, i) =>
                        <React.Fragment key={i}>
                            <th>{field}</th>
                            {this.props.reconcile_field == field &&
                                <th>Select charity</th>}
                        </React.Fragment>
                    )
                }
            </tr>
        )
    }
}

export default connect(mapStateToProps)(ReconcileHeaderRow);
