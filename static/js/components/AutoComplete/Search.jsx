import React from "react";

export default class SearchAutoComplete extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            "results": [],
            "loading": false,
            "q": props.value
        }
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(e) {
        const element = this;
        this.setState({ "q": e.target.value });
        if (this.state.q.length > 2) {
            this.setState({ "loading": true });
            fetch(`/autocomplete?q=${this.state.q}`)
                .then(function (response) {
                    return response.json();
                })
                .then(function (myJson) {
                    element.setState({
                        "results": myJson["results"],
                        "loading": false
                    });
                });
        } else {
            this.setState({
                "results": []
            })
        }
    }

    getHighlightedText(text, highlight) {
        // Split text on higlight term, include term itself into parts, ignore case
        // https://stackoverflow.com/questions/29652862/highlight-text-using-reactjs
        var parts = text.split(new RegExp(`(${highlight})`, 'gi'));
        return <span>{parts.map((part, i) => part.toLowerCase() === highlight.toLowerCase() ? <b key={i}>{part}</b> : part)}</span>;
    }

    render() {
        return (
            <div className="dropdown is-active" style={{ display: 'block', width: '100%' }}>
                <div className="dropdown-trigger field has-addons has-addons-centered">
                    <div className={(this.state.loading ? "is-loading" : "") + " control is-expanded"}>
                        <input value={this.state.q}
                            name="q"
                            className="input is-large is-fullwidth"
                            placeholder="Search for a charity name or number"
                            type="text"
                            onChange={this.handleChange}
                            aria-haspopup="true"
                            aria-controls="dropdown-menu"
                            autoComplete="off" />
                    </div>
                    <div className="control">
                        <input type="submit" value="Search" className="button is-info is-large" />
                    </div>
                </div>
                {this.state.results.length > 0 &&
                    <div className="dropdown-menu" id="dropdown-menu" role="menu" style={{ width: '100%' }}>
                        <div className="dropdown-content">
                            {this.state.results.map((result, i) =>
                                <React.Fragment key={i}>
                                    {i > 0 && <hr className="dropdown-divider" />}
                                    <a href={"/charity/" + result.value} data-value={result.value} data-label={result.label} className="dropdown-item">
                                        <div className="columns">
                                            <div className="column">{this.getHighlightedText(result.label, this.state.q)}</div>
                                            <div className="column is-italic has-text-grey is-narrow">{result.value}</div>
                                        </div>
                                    </a>
                                </React.Fragment>
                            )}
                        </div>
                    </div>
                }
            </div>
        )
    }
}