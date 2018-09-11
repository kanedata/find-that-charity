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
            <div className="field is-grouped">
                <span className="tags has-addons" style={ {display: 'inline', marginBottom: '0px'} }>
                    <span className="tag">                        
                        <span className="icon is-small has-text-success">
                            <i className="fa fa-check"></i>
                        </span>{' '}
                    </span>
                    <span className="tag is-success">Matched</span>
                </span>
                <span className="field" style={{ paddingLeft: '0.5rem', paddingRight: '0.5rem', marginBottom: '0px'} }>
                    {this.props.result.source.known_as}{' '}
                    (<a href={"/charity/" + this.props.result.id} target="_blank">{this.props.result.id}</a>)
                </span>
                <span className="field has-addons" style={ {marginBottom: '0px'}}>
                    <p className="control" style={{ marginBottom: '0px' }}>
                        <a className="button is-small is-link is-outlined" href="#" onClick={this.unmatch} >Unmatch</a>
                    </p>
                    {this.state.show_preview &&
                        <p className="control" style={{ marginBottom: '0px' }}><a className="button is-small is-link" href="#" onClick={this.hidePreview}>hide preview</a></p>}
                    {!this.state.show_preview &&
                        <p className="control" style={{ marginBottom: '0px' }}><a className="button is-small is-link is-outlined" href="#" onClick={this.showPreview}>preview</a></p>}
                </span>
                {this.state.show_preview &&
                    <ReconcilePreview result={this.props.result.source} id={this.props.result.id} hidePreview={this.hidePreview} />}
            </div>
        )
    }
}