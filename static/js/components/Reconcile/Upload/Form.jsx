import React from "react";
import { connect } from "react-redux";
import Papa from "papaparse"

import { set_data, set_stage, set_file } from "../../../actions/Actions"
import FileUpload from "./FileUpload";
import SubmitForm from "./SubmitForm";
import Guidance from "./Guidance";

const mapStateToProps = (state) => {
    return {
        file: state.file
    }
}

const mapDispatchToProps = dispatch => {
    return {
        setData: (rows, fields) => {
            dispatch(set_data(rows, fields));
        },
        setStage: stage => {
            dispatch(set_stage(stage))
        },
        setFile: stage => {
            dispatch(set_file(stage))
        }
    }
}

class ReconcileForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            errors: []
        }
        this.getFileData = this.getFileData.bind(this);
        this.fileInput = React.createRef();
    }

    getFileData(stage){
        const form = this;
        Papa.parse(this.fileInput.current.files[0], {
            complete: function (results, file) {
                form.props.setData(results.data, results.meta.fields);
                form.props.setStage(stage);
                form.props.setFile(file);
                // @TODO save the file configuration for making sure the download looks the same
            },
            skipEmptyLines: true,
            header: true,
        })
    }

    render() {
        return (
            <div className="columns">
                <div className="column is-two-thirds">
                    <div className="content">
                        <form>
                            <FileUpload componentReference={this.fileInput} />
                            {/* TODO:  add textarea to paste data in */}
                            {/* TODO:  add CSV options */}
                            <SubmitForm getFileData={this.getFileData} />
                        </form>
                    </div>
                </div>
                <div className="column">
                    <div className="content">
                        <Guidance errors={this.state.errors} />
                    </div>
                </div>
            </div>
        )
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(ReconcileForm);
