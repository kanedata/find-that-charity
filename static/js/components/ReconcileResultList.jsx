import React from "react";
import {connect} from "react-redux";

import ReconcileResultMatched from "./ReconcileResultMatched"
import ReconcileResult from "./ReconcileResult"
import AutoCompleteReconcile from "./AutoCompleteReconcile"

import { match_result, unmatch_result } from "../actions/Actions"

const mapStateToProps = (state, ownProps) => {
    var row = state.data[ownProps.rowid];
    var matched = null;
    var charity_id = row[state.charity_number_field];
    if(!charity_id){
        charity_id = ownProps.matches[0].match ? ownProps.matches[0].id : charity_id;
    }

    if(charity_id){
        matched = ownProps.matches.find(el => el.id == charity_id );
        matched = matched ? matched : { 
            id: charity_id, 
            source: {
                known_as: row[state.reconcile_field]
            }
        }
    }
    return {...ownProps, matched: matched }
}

const mapDispatchToProps = dispatch => {
    return {
        matchResult: (rowid, result) => {
            dispatch(match_result(rowid, result));
        },
        unmatchResult: rowid => {
            dispatch(unmatch_result(rowid));
        }
    }
}

class ReconcileResultList extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            confirmed: null,
            show_matches: 3,
            show_suggest: false,
            show_preview: false
        };
        this.selectInput = this.selectInput.bind(this);
        this.unmatch = this.unmatch.bind(this);
        this.showMore = this.showMore.bind(this);
        this.showFewer = this.showFewer.bind(this);
        this.showSuggest = this.showSuggest.bind(this);
        this.hideSuggest = this.hideSuggest.bind(this);
    }

    selectInput(result) {
        this.props.matchResult(this.props.rowid, result);
    }

    unmatch(result) {
        this.props.unmatchResult(this.props.rowid);
    }

    showMore(e) {
        e.preventDefault();
        this.setState({ show_matches: Math.min(this.props.matches.length, this.state.show_matches + 3) })
    }

    showFewer(e) {
        e.preventDefault();
        this.setState({ show_matches: Math.max(this.state.show_matches - 3, 3) })
    }

    showSuggest(e) {
        e.preventDefault();
        this.setState({ show_suggest: true })
    }

    hideSuggest(e) {
        e.preventDefault();
        this.setState({ show_suggest: false })
    }

    render() {
        if (this.props.matched) {
            return <ReconcileResultMatched result={this.props.matched} unmatch={this.unmatch} />;
        }
        return (
            <div>
                {this.props.matches.map((match, i) =>
                    i < this.state.show_matches &&
                    <ReconcileResult key={i} result={match} selectInput={this.selectInput} />
                )}
                <span className="is-size-7">
                    <span className="has-text-grey">{this.state.show_matches + " of " + this.props.matches.length + " results"}</span>
                    {' '}
                    {this.props.matches.length > this.state.show_matches &&
                        <a href="#" onClick={this.showMore}>[more]</a>}
                    {' '}
                    {this.state.show_matches > 3 &&
                        <a href="#" onClick={this.showFewer}>[fewer]</a>}
                    {' '}
                    {this.state.show_suggest &&
                        <a href="#" onClick={this.hideSuggest}>[hide search]</a>}
                    {' '}
                    {!this.state.show_suggest &&
                        <a href="#" onClick={this.showSuggest}>[show search]</a>}
                </span>
                {this.state.show_suggest &&
                    <div>
                        <AutoCompleteReconcile selectInput={this.selectInput} />
                    </div>}
            </div>
        );
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(ReconcileResultList);
