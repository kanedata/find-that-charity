import React from "react";
import ReconcilePreview from "./ReconcilePreview";

export default class ReconcileResultMatched extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            "show_preview": false
        }
        this.unmatch = this.unmatch.bind(this);
        this.showPreview = this.showPreview.bind(this);
        this.hidePreview = this.hidePreview.bind(this);
    }

    unmatch(e) {
        e.preventDefault();
        this.props.unmatch(this.props.result);
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
                <span className="tag is-success">Matched</span>
                {' '}{this.props.result.source.known_as}{' '}
                (<a href={"/charity/" + this.props.result.id} target="_blank">{this.props.result.id}</a>){' '}
                <span className="has-text-grey is-size-7">
                    [<a href="#" onClick={this.unmatch} >Unmatch</a>]
                    {' '}
                    {this.state.show_preview &&
                        <a href="#" onClick={this.hidePreview}>[hide preview]</a>}
                    {' '}
                    {!this.state.show_preview &&
                        <a href="#" onClick={this.showPreview}>[preview]</a>}
                </span>
                {this.state.show_preview &&
                    <ReconcilePreview result={this.props.result.source} id={this.props.result.id} hidePreview={this.hidePreview} />}
            </div>
        )
    }
}