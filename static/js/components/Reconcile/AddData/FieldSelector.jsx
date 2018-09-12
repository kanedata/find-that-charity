import React from 'react'

import { set_field_names, add_charity_numbers } from "../../../actions/Actions"

class FieldSelector extends React.Component {
    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(event){
        this.props.dispatch(set_field_names(this.props.name, event.target.value));
    }

    render() {
        return (
            <div className="field">
                <label className="label">{this.props.label}</label>
                <div className="control">
                    <div className="select is-fullwidth">
                        <select value={this.props.field_value} onChange={this.handleChange}>
                            <option value="">-- Select value --</option>
                            {this.props.fields.map((field, i) =>
                                <option value={field} key={i}>{field}</option>
                            )}
                        </select>
                    </div>
                </div>
            </div>
        )
    }
}

export default FieldSelector;