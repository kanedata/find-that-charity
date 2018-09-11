import React from "react";
import { connect } from "react-redux";
import { toggle_field } from "../../actions/Actions"

const mapStateToProps = (state) => {
    return {
        fields: state.fields,
        hidden_fields: state.hidden_fields,
        reconcile_field: state.reconcile_field
    };
};

const mapDispatchToProps = dispatch => {
    return {
        toggleField: field => {
            dispatch(toggle_field(field))
        },
    }
}

class ReconcileFieldFilter extends React.Component {
    constructor(props) {
        super(props);
        this.fieldClick = this.fieldClick.bind(this);
    }

    fieldClick(ev){
        this.props.toggleField(ev.target.value);
    }

    render() {
        return (
            <div className="field is-horizontal">
                <div className="field-label">
                    <label className="label">Show/hide columns</label>
                </div>
                <div className="field-body">
                    <div className="field is-grouped is-grouped-multiline">
                        {this.props.fields.map((field, i) =>
                            <p className="control" key={i}>
                                <label className="checkbox" disabled={this.props.reconcile_field == field}>
                                    <input type="checkbox" 
                                        value={field}  
                                        onChange={this.fieldClick}
                                        disabled={this.props.reconcile_field == field}
                                        defaultChecked={this.props.hidden_fields.indexOf(field)} />
                                    {' ' + field}
                                </label>
                            </p>
                        )
                        }
                    </div>
                </div>
            </div>
        )
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(ReconcileFieldFilter);
