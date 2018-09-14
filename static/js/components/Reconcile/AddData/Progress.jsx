import React from 'react'

class Progress extends React.Component {
    constructor(props) {
        super(props);
        this.getTotalProgress = this.getTotalProgress.bind(this);
    }

    getTotalProgress(){
        return this.props.organisationsFound + this.props.organisationsNotFound + this.props.fetchErrors;
    }

    render() {
        return (
            <div>
                <h2 class="title is-3">Progress</h2>
                <div>
                    {this.props.maxProgress} unique values in the
                    <code>{this.props.charity_number_field}</code>
                    field
                </div>
                <progress className="progress is-large is-primary"
                    value={this.getTotalProgress()}
                    max={this.props.maxProgress}>
                    {this.getTotalProgress()}
                </progress>
                <ul>
                    <li>{this.props.organisationsFound} organisations found</li>
                    <li>{this.props.organisationsNotFound} organisations not found</li>
                    <li>{this.props.fetchErrors} errors fetching</li>
                </ul>
            </div>
        )
    }
}

export default Progress;