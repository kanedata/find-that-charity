import React from 'react'

class SubmitForm extends React.Component {
    constructor(props) {
        super(props);
        this.toAddData = this.toAddData.bind(this);
    }

    toAddData(event) {
        event.preventDefault();
        this.props.getFileData('adddata');
    }
    
    render() {
        return (
            <div className="field is-grouped">
                <div className="control">
                    <input type="submit" value="Add charity data" onClick={this.toAddData} className="button is-link" />
                </div>
            </div>
        )
    }
}

export default SubmitForm;