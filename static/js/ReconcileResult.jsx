import React from "react";

export default class ReconcileResult extends React.Component {
    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(e) {
        this.props.selectInput(this.props.result);
    }

    render() {
        return (
            <div>
                <label className="is-size-6">
                    <input type="radio" className="reconcile_choice" name="reconcile_choice_" value={this.props.result.id} onChange={this.handleChange} />
                    {' '}{this.props.result.source.known_as}{' '}
                    (<a href={"/charity/" + this.props.result.id} target="_blank">{this.props.result.id}</a>){' '}
                    <span className="has-text-grey is-size-7">[{this.props.result.score}]</span>
                </label>
            </div>
        )
    }
}