import React from 'react'

class Guidance extends React.Component {
    render() {
        return (
            <React.Fragment>
                {this.props.errors &&
                    this.props.errors.map((error) => 
                    <div className="notification is-danger">
                        <button className="delete"></button>
                        <strong>Error:</strong> { error }
                    </div>
                    )
                }
                <p>
                    Use this form to add more data to a CSV containing data about charities. 
                    Your file will need to contain charity numbers for these charities.
                </p>
                <article className="message is-warning">
                    <div className="message-header">
                        Data protection
                    </div>
                    <div className="message-body">
                        Your data file won't leave your computer, although the names and charity
                        numbers of charities in your file will be sent as web requests to findthatcharity.uk.
                        These web requests may be stored in logs on the find that charity server, but
                        no other information about your file will be stored.
                    </div>
                </article>
            </React.Fragment>
        )
    }
}

export default Guidance;