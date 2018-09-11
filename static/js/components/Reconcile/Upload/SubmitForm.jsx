import React from 'react'

class SubmitForm extends React.Component {
    constructor(props) {
        super(props);
        this.toReconcile = this.toReconcile.bind(this);
        this.toAddData = this.toAddData.bind(this);
    }

    toReconcile(event) {
        event.preventDefault();
        this.props.getFileData('namefield');
    }

    toAddData(event) {
        event.preventDefault();
        this.props.getFileData('adddata');
    }
    
    render() {
        return (
            <React.Fragment>
                <label className="label">Choose the next step</label>
                <div className="field is-grouped">
                    <div className="control">
                        <input type="submit" value="I need to add charity numbers" onClick={this.toReconcile} className="button is-link" />
                        <p className="help">You'll need to select a column<br />containing the charity name</p>
                    </div>
                    <div className="control">
                        <input type="submit" value="My data has charity numbers" onClick={this.toAddData} className="button is-link" />
                    </div>
                </div>
            </React.Fragment>
        )
    }
}

export default SubmitForm;