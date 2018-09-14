import React from "react";
import { connect } from "react-redux";
import file_download from 'js-file-download';
import Papa from 'papaparse'

import { add_charity_numbers, add_org_record, set_stage } from "../../../actions/Actions"
import FieldSelector from "./FieldSelector";
import FieldsToAdd from "./FieldsToAdd";
import Progress from "./Progress";

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
        stage: state.stage,
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
        setStage: stage => {
            dispatch(set_stage(stage))
        },
    }
}

class ReconcileAddData extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loading: false,
            maxProgress: 1,
            organisationsFound: 0,
            organisationsNotFound: 0,
            fetchErrors: 0,
        }
        this.processCharity = this.processCharity.bind(this);
        this.fetchData = this.fetchData.bind(this);
    }

    // Fetch the organisation details based on a charity number
    fetchData(event) {
        event.preventDefault();

        // find all the organisation identifiers in the data
        // based on the charity number field that has been selected
        let charity_numbers = this.getCharityNumbers();
        this.props.addCharityNumbers(charity_numbers);
        this.setState({
            loading: true,
            maxProgress: charity_numbers.size,
            organisationsFound: 0,
            organisationsNotFound: 0,
            fetchErrors: 0,
        })

        let comp = this;
        if(charity_numbers){

            // Promise which will return when all the charity data has been fetched
            Promise.all([...charity_numbers].map(charity_number => {

                // work out the URL to fetch charity data from
                let charity_url = encodeURI(`/charity/${charity_number}.json`);

                // do the actual fetching of the data
                // @TODO handle errors here
                return fetch(charity_url)
                    .then(function (response) {
                        if(response.ok){
                            return response.json();
                        }
                        comp.setState(function (prevState) {
                            return { organisationsNotFound: prevState.organisationsNotFound + 1 }
                        });
                    })
                    .then(function (charity_data) {
                        // when the data has been fetched store the record
                        comp.props.addOrgRecord(
                            charity_number, 
                            comp.processCharity(charity_data)
                        )
                        comp.setState(function (prevState) {
                            return {organisationsFound: prevState.organisationsFound + 1}
                        });
                    })
                    .catch(function(error){
                        comp.setState(function (prevState) {
                            return { fetchErrors: prevState.fetchErrors + 1 }
                        });
                    });

            // only called when all the data has been fetched from the API
            })).then(function(values){
                comp.props.setStage('download');
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
                            <div className="control">
                                <input type="submit" value="Add data and download" onClick={this.fetchData} className="button is-link" />
                                {/* @TODO add cancel button to return to first page */}
                            </div>
                        </form>
                    </div>
                </div>
                <div className="column">
                    {this.state.loading && 
                        <Progress charity_number_field={this.props.charity_number_field}
                                  maxProgress={this.state.maxProgress}
                                  organisationsFound={this.state.organisationsFound}
                                  organisationsNotFound={this.state.organisationsNotFound}
                                  fetchErrors={this.state.fetchErrors} />
                    }
                </div>
            </div>
        )
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(ReconcileAddData);