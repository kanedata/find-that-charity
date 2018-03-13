import React from "react";

export default class MatchedReconcileResult extends React.Component {
    constructor(props) {
        super(props);
        this.unmatch = this.unmatch.bind(this);
    }

    unmatch(e) {
        e.preventDefault();
        this.props.unmatch(this.props.result);
    }

    render() {
        return (
            <div>
                <span className="tag is-success">Matched</span>
                {' '}{this.props.result.source.known_as}{' '}
                (<a href={"/charity/" + this.props.result.id} target="_blank">{this.props.result.id}</a>){' '}
                <span className="has-text-grey is-size-7">[<a href="#" onClick={this.unmatch} >Unmatch</a>]</span>
            </div>
        )
    }
}