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
        e.preventDefault();
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
            <React.Fragment>
                <div className="buttons" htmlFor={this.id} style={ {margin: '0px'} }>
                    <a href="#" onClick={this.handleChange} className="button is-small is-primary is-outlined">
                        <span className="icon is-small">
                            <i className="fa fa-check"></i>
                        </span>
                        <span className="has-text-dark">{this.props.result.source.known_as + " (" + this.props.result.id + ")"})</span>
                        <span className="is-italic has-text-grey">
                            &nbsp;[{this.props.result.score}]
                        </span>
                    </a>
                    {this.state.show_preview &&
                    <a className="button is-small is-link" href="#" onClick={this.hidePreview}>Hide preview</a>}
                    {!this.state.show_preview &&
                    <a className="button is-small is-link is-outlined" href="#" onClick={this.showPreview}>Preview</a>}
                </div>
                {this.state.show_preview &&
                    <ReconcilePreview result={this.props.result.source} id={this.props.result.id} hidePreview={this.hidePreview} />}
            </React.Fragment>
        )
    }
}