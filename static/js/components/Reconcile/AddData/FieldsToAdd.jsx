import React from 'react'

import { set_fields_to_add } from "../../../actions/Actions"

export const potentialFieldsToAdd = [
    { slug: 'postcode', name: 'Postcode' },
    { slug: 'latest_income', name: 'Latest income' },
    { slug: 'known_as', name: 'Name' },
]

class FieldsToAdd extends React.Component {
    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(event) {
        let fieldsToAdd = this.props.fieldsToAdd;
        if (event.target.checked) {
            if (!fieldsToAdd.includes(event.target.value)) {
                fieldsToAdd = fieldsToAdd.concat([event.target.value]);
            }
        } else {
            fieldsToAdd = fieldsToAdd.filter(e => e !== event.target.value);
        }
        this.props.dispatch(set_fields_to_add(fieldsToAdd));
    }

    render() {
        return (
            <div className="field">
                <label className="label">Select fields to add</label>
                <div className="control">
                    {potentialFieldsToAdd.map((field, i) =>
                        <div key={i}>
                            <label className="checkbox">
                                <input type="checkbox" 
                                    value={field.slug} 
                                    checked={this.props.fieldsToAdd.includes(field.slug)}
                                    onChange={this.handleChange} /> {field.name}
                            </label>
                        </div>
                    )}
                </div>
            </div>
        )
    }
}

export default FieldsToAdd;