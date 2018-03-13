import React from "react";

export default class ReconcilePreview extends React.Component {
    constructor(props) {
        super(props);
        this.deleteSelf = this.deleteSelf.bind(this);
    }

    deleteSelf(e) {
        this.props.hidePreview(e);
    }

    render() {
        return (
            <div id="quickviewDefault" className="quickview is-active">
                <header className="quickview-header" style={ {padding: '1rem'} }>
                    <h3 style={ {marginBottom: '0px'} }>{this.props.result.known_as}</h3>
                    <span className="delete" data-dismiss="quickview" onClick={this.deleteSelf}></span>
                </header>

                <div className="quickview-body" style={ {padding: '1rem'} }>
                    <div className="quickview-block" style={ {height: '100%' } }>
                        <iframe src={"/preview/charity/" + this.props.id + "?hide_title"} style={{ height: '100%', display: 'block', width: '100%' }} seamless="seamless" scrolling="no" >
                        </iframe>
                    </div>
                </div>

                <footer className="quickview-footer">

                </footer>
            </div>
        )
    }
}