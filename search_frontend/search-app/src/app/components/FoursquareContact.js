import React from "react";

export class FoursquareContact extends React.Component {
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

FoursquareContact.propTypes = {
    foursquare_resource_locator : React.PropTypes.string,
    org_name : React.PropTypes.string,
    description : React.PropTypes.string,
    address : React.PropTypes.string,
    country : React.PropTypes.string,
    // state : React.PropTypes.string,
    postal_code : React.PropTypes.number,
    contact_no : React.PropTypes.string,
    // industry : React.PropTypes.string,
    fan_count : React.PropTypes.number,
    hours : React.PropTypes.string,
    link : React.PropTypes.string,
    longitude : React.PropTypes.string,
    latitude : React.PropTypes.string
}
