import React from 'react'

class FileUpload extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            filename: null,
        }
        this.setFileName = this.setFileName.bind(this);
    }

    setFileName(event) {
        event.preventDefault();
        this.setState({
            filename: this.props.componentReference.current.files[0].name
        })
    }

    render() {
        return (
            <div className="field">
                <label className="label">CSV File</label>
                <div className="control">
                    <div className="file has-name is-fullwidth">
                        <label className="file-label">
                            <input className="file-input" type="file" 
                                   ref={this.props.componentReference} 
                                   onChange={this.setFileName} 
                                   name="uploadcsv" 
                                   id="uploadcsv" 
                                   accept=".csv,text/csv" />
                            <span className="file-cta">
                                <span className="file-label">
                                    Select a file…
                                </span>
                            </span>
                            {this.state.filename &&
                                <span className="file-name" id="uploadcsv-filename">{this.state.filename}</span>
                            }
                        </label>
                    </div>
                </div>
                <p className="help">Must be a valid CSV file.</p>
            </div>
        )
    }
}

export default FileUpload;