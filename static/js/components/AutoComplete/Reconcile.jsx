import React from "react";

export default class AutoComplete extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            "results": [],
            "loading": false,
            "q": ""
        }
        this.handleChange = this.handleChange.bind(this);
        this.selectInput = this.selectInput.bind(this);
    }

    selectInput(e) {
        e.preventDefault();
        this.props.selectInput({
            "id": e.target.closest("a").dataset.value,
            "source": {
                "known_as": e.target.closest("a").dataset.label
            }
        });
    }

    handleChange(e) {
        const element = this;
        this.setState({ "q": e.target.value });
        if (e.target.value.length > 2) {
            this.setState({ "loading": true });
            fetch(`/autocomplete?q=${e.target.value}`)
            .then(function (response) {
                return response.json();
            })
            .then(function (myJson) {
                element.setState({
                    "results": myJson["results"],
                    "loading": false
                });
            });
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
            <div className="dropdown is-active" style={{ display: 'block' }}>
                <div className="dropdown-trigger">
                    <div className={(this.state.loading ? "is-loading" : "") + " control"}>
                        <input className="input is-fullwidth" type="text" onChange={this.handleChange} aria-haspopup="true" aria-controls="dropdown-menu" />
                    </div>
                </div>
                {this.state.results.length > 0 &&
                    <div className="dropdown-menu" id="dropdown-menu" role="menu" style={{ width: '100%' }}>
                        <div className="dropdown-content">
                            {this.state.results.map((result, i) =>
                                <React.Fragment key={i}>
                                    {i > 0 && <hr className="dropdown-divider" />}
                                    <a href="#" data-value={result.value} data-label={result.label} className="dropdown-item" onClick={this.selectInput}>
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