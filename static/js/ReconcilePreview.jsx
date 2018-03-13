import React from "react";

export default class ReconcilePreview extends React.Component {
    render() {
        return (
            <article className="message is-small">
                <div className="message-header">
                    <p>Small message</p>
                    <button className="delete is-small" aria-label="delete"></button>
                </div>
                <div className="message-body">
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit. <strong>Pellentesque risus mi</strong>, tempus quis placerat ut, porta nec nulla.Nullam gravida purus diam, et dictum <a>felis venenatis</a> efficitur. Aenean ac <em>eleifend lacus</em>, in mollis lectus.
          </div>
            </article>
        )
    }
}