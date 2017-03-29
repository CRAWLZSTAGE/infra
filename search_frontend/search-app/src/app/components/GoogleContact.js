import React from "react";

export class GoogleContact extends React.Component {
    constructor(props) {
        super();
    }

    call_me() {
        console.log("TBC")
    }

    render() {
        return (
            <div>
                <h3>Hello {this.props.org_name}!</h3>
                <button onClick={this.call_me.bind(this)} className="btn btn-success">Call me!</button>
            </div>
        );
    }
}

GoogleContact.propTypes = {
    google_resource_locator : React.PropTypes.string,
    org_name : React.PropTypes.string,
    address : React.PropTypes.string,
    country : React.PropTypes.string,
    postal_code : React.PropTypes.number,
    contact_no : React.PropTypes.string,
    industry : React.PropTypes.string,
    rating : React.PropTypes.number,
    link : React.PropTypes.string,
    longitude : React.PropTypes.string,
    latitude : React.PropTypes.string,
    intl_number_with_plus : React.PropTypes.string
}

