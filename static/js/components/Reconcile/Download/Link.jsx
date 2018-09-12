import React from "react";
import { connect } from "react-redux";
import file_download from 'js-file-download';
import Papa from 'papaparse'

import {potentialFieldsToAdd} from '../AddData/FieldsToAdd'

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

class ReconcileDownloadData extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            enhancedData: [],
            allFields: [],
        }
        this.getFileData = this.getFileData.bind(this);
        this.getFieldNameLookup = this.getFieldNameLookup.bind(this);
        this.getFields = this.getFields.bind(this);
        this.downloadData = this.downloadData.bind(this);
    }

    componentDidMount(){
        let field_renames = this.getFieldNameLookup();
        this.setState({
            enhancedData: this.getFileData(field_renames),
            allFields: this.getFields(field_renames),
        })
    }

    getFields(field_renames) {
        return [...this.props.fields, ...this.props.fields_to_add.map((f) => field_renames[f] )];

    }

    getFileData(field_renames){
        return this.props.data.map((data) => {
            // get the charity number based on the charity number field
            let charity_number = data[this.props.charity_number_field];

            // fetch the data based on the charity number
            let extra_data = {};
            Object.keys(field_renames).forEach(f => {
                let new_field_name = field_renames[f];
                if (this.props.org_data[charity_number]){
                    extra_data[new_field_name] = this.props.org_data[charity_number][f];
                } else {
                    extra_data[new_field_name] = null;
                }
            })

            // return the original data with the new data merged in
            // if two field names are the same then the new fields are used
            return Object.assign({}, extra_data, data);
        })
    }

    getFieldNameLookup(){
        let field_names = {}
        this.props.fields_to_add.forEach(f => {
            if (this.props.fields.includes(f)){
                field_names[f] = `${f}_new`;
            } else {
                field_names[f] = f;
            }
        });
        return field_names;
    }

    // Fetch the organisation details based on a charity number
    downloadData(event) {
        event.preventDefault();

        // turn it into a CSV string
        let file_contents = Papa.unparse({
            fields: this.state.allFields,
            data: this.state.enhancedData
        });
        
        // sent the file to the user to download
        // @TODO: work out better filename 
        file_download(file_contents, 'test.csv', 'text/csv');

    }

    render() {
        let preview_rows = 10;
        let number_format = new Intl.NumberFormat().format
        return (
            <div className="columns">
                <div className="column is-one-fifth">
                    <div className="content">
                        <form>
                            <div className="control">
                                <input type="button" value="Download your data" 
                                    onClick={this.downloadData} 
                                    className="button is-link is-fullwidth" />
                                {/* @TODO add cancel button to return to first page */}
                            </div>
                        </form>
                    </div>
                </div>
                <div className="column no-overflow" style={{overflow: "hidden"}}>
                    {this.state.enhancedData &&
                    <React.Fragment>
                        <h2 className="title is-2">Preview data</h2>
                        <h3 className="subtitle">
                        {this.state.enhancedData.length <= preview_rows ? (
                            <React.Fragment>
                                Showing all {number_format(this.state.enhancedData.length)} rows
                            </React.Fragment>
                        ) : (
                            <React.Fragment>
                                Showing {number_format(preview_rows)} of {number_format(this.state.enhancedData.length)} rows
                            </React.Fragment>
                        )}
                        </h3>
                        <div style={{overflow: "auto"}}>
                            <table className="table is-striped is-narrow is-fullwidth preview-table">
                                <thead>
                                    <tr>
                                        {this.state.allFields.map((f, i) =>
                                            <th key={i}>{f}</th>    
                                        )}
                                    </tr>
                                </thead>
                                <tbody>
                                    {this.state.enhancedData.slice(0, preview_rows).map((org, i) =>
                                        <tr key={i}>
                                            {this.state.allFields.map((f, i) =>
                                                <td key={i}>
                                                    <div style={{maxHeight: '48px', overflowY: 'hidden'}}>
                                                        {org[f]}
                                                    </div>
                                                </td>
                                            )}
                                        </tr>  
                                    )}
                                </tbody>
                            </table>
                        </div>
                        {/* <pre>
                            {Papa.unparse({
                                fields: this.state.allFields,
                                data: this.state.enhancedData.slice(0, preview_rows)
                            })}
                        </pre> */}
                    </React.Fragment>
                }
                </div>
            </div>
        )
    }
}

export default connect(mapStateToProps)(ReconcileDownloadData);