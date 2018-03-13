import React from "react";
import ReconcilePreview from "./ReconcilePreview";

export default class ReconcileResult extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            "show_preview": false
        }
        this.handleChange = this.handleChange.bind(this);
        this.showPreview = this.showPreview.bind(this);
        this.hidePreview = this.hidePreview.bind(this);
    }

    handleChange(e) {
        this.props.selectInput(this.props.result);
    }

    showPreview(e) {
        e.preventDefault();
        this.setState({ show_preview: true })
    }

    hidePreview(e) {
        e.preventDefault();
        this.setState({ show_preview: false })
    }

    render() {
        return (
            <div>
                <label className="is-size-6">
                    <input type="radio" className="reconcile_choice" name="reconcile_choice_" value={this.props.result.id} onChange={this.handleChange} />
                    {' '}{this.props.result.source.known_as}{' '}
                    (<a href={"/charity/" + this.props.result.id} target="_blank">{this.props.result.id}</a>){' '}
                    <span className="has-text-grey is-size-7">
                        [{this.props.result.score}]
                        {' '}
                        {this.state.show_preview &&
                            <a href="#" onClick={this.hidePreview}>[hide preview]</a>}
                        {' '}
                        {!this.state.show_preview &&
                            <a href="#" onClick={this.showPreview}>[preview]</a>}
                    </span>
                </label>
                {this.state.show_preview &&
                    <ReconcilePreview result={this.props.result.source} id={this.props.result.id} hidePreview={this.hidePreview} />}
            </div>
        )
    }
}