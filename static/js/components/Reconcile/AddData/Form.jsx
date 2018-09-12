import React from "react";
import { connect } from "react-redux";
import file_download from 'js-file-download';
import Papa from 'papaparse'

import { add_charity_numbers, add_org_record } from "../../../actions/Actions"
import FieldSelector from "./FieldSelector";
import FieldsToAdd from "./FieldsToAdd";
import { potentialFieldsToAdd } from "./FieldsToAdd";

const mapStateToProps = (state) => {
    return { 
        fields: state.fields,
        data: state.data,
        charity_number_field: state.charity_number_field,
        org_id_field: state.org_id_field,
        file: state.file,
        charity_numbers: state.charity_numbers,
        fields_to_add: state.fields_to_add,
        org_data: state.org_data,
        progress: state.progress,
        loading: state.loading,
    };
};

const mapDispatchToProps = dispatch => {
    return {
        dispatch,
        addCharityNumbers: charity_numbers => {
            dispatch(add_charity_numbers(charity_numbers));
        },
        addOrgRecord: (charity_number, record) => {
            dispatch(add_org_record(charity_number, record))
        },
    }
}

class ReconcileAddData extends React.Component {
    constructor(props) {
        super(props);
        this.processCharity = this.processCharity.bind(this);
        this.fetchData = this.fetchData.bind(this);
    }

    // Fetch the organisation details based on 
    fetchData(event) {
        event.preventDefault();
        let charity_numbers = this.getCharityNumbers();
        this.props.addCharityNumbers(charity_numbers);
        let comp = this;
        if(charity_numbers){
            Promise.all([...charity_numbers].map(charity_number => {
                let charity_url = encodeURI(`/charity/${charity_number}.json`);
                return fetch(charity_url)
                    .then(function (response) {
                        return response.json();
                    })
                    .then(function (charity_data) {
                        comp.props.addOrgRecord(
                            charity_number, 
                            comp.processCharity(charity_data)
                        )
                    });
            })).then(function(values){

                // go through each row and return a new object with the extra fields added
                let file_data = comp.props.data.map((data) => {
                    // get the charity number based on the charity number field
                    let charity_number = data[comp.props.charity_number_field];

                    // fetch the data based on the charity number
                    let extra_data = comp.props.org_data[charity_number];

                    // return the original data with the new data merged in
                    // if two field names are the same then the new fields are used
                    return Object.assign({}, extra_data, data);
                })

                // get the field names
                let field_names = [...comp.props.fields, ...comp.props.fields_to_add]

                // turn it into a CSV string
                let file_contents = Papa.unparse({
                    fields: field_names,
                    data: file_data
                });
                
                // sent the file to the user to download
                // @TODO: work out better filename 
                file_download(file_contents, 'test.csv', 'text/csv');
            });
        }

    }

    getCharityNumbers(){
        return new Set(this.props.data.map((record, i) => {
            if (record[this.props.charity_number_field] != "") {
                return record[this.props.charity_number_field]
            }
        }).filter((k) => k != undefined));
    }

    processCharity(charity_data){
        let new_fields = {}
        this.props.fields_to_add.forEach(f => {
            if(f=='postcode'){
                new_fields[f] = charity_data["geo"]["postcode"];
            } else {
                new_fields[f] = charity_data[f];
            }
        });
        return new_fields;
    }

    /*
    Need to:

     -Y select charity number field
     -Y select fields to add to data
     - make requests to get the data (only send request for unique charity numbers then get dictionary)
     - save the additional columns in the state
    */

    render() {
        return (
            <div className="columns">
                <div className="column is-one-third">
                    <div className="content">
                        <form>
                            <FieldSelector label="Select charity number field"
                                name="charity_number_field"
                                field_value={this.props.charity_number_field}
                                fields={this.props.fields}
                                dispatch={this.props.dispatch} />
                            {/* <FieldSelector label="Select Org ID field"
                                name="org_id_field"
                                field_value={this.props.org_id_field}
                                fields={this.props.fields}
                                dispatch={this.props.dispatch} /> */}
                            <FieldsToAdd fieldsToAdd={this.props.fields_to_add}
                                dispatch={this.props.dispatch} />
                            {this.props.charity_numbers &&
                            <div>
                                {this.props.charity_numbers.size} charity numbers found
                            </div>}
                            <div className="control">
                                <input type="submit" value="Add data and download" onClick={this.fetchData} className="button is-link" />
                            </div>
                        </form>
                    </div>
                </div>
                <div className="column">
                {this.props.org_data &&
                    <div>
                        <h2>Fetched data</h2>
                        <table className="table is-striped is-narrow">
                            <thead>
                                <tr>
                                    <th>Charity number</th>
                                    {potentialFieldsToAdd.filter(f => this.props.fields_to_add.includes(f.slug))
                                        .map((f, i) =>
                                        <th key={i}>{f.name}</th>    
                                    )}
                                </tr>
                            </thead>
                            <tbody>
                            {Object.keys(this.props.org_data).map((org, i) =>
                                <tr key={i}>
                                    <th>{org}</th>
                                    {potentialFieldsToAdd.filter(f => this.props.fields_to_add.includes(f.slug))
                                        .map((f, i) =>
                                            <td key={i}>{this.props.org_data[org][f.slug]}</td>
                                    )}
                                </tr>  
                            )}
                            </tbody>
                        </table>
                        <pre>{JSON.stringify(this.props.org_data, null, '\t')}</pre>
                    </div>
                }
                </div>
            </div>
        )
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(ReconcileAddData);