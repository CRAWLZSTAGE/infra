import React from "react";
import { GenericContact } from "./GenericContact";

export class FoursquareContact extends React.Component {
    constructor(props) {
        super(props);
    } 

    render() {
        var allFoursquareContacts = []
        if (this.props.foursquareContacts != null){
            allFoursquareContacts = this.props.foursquareContacts.map((foursquareContact) => {
                return (
                    <div key={foursquareContact.foursquare_resource_locator}>
                        <GenericContact contactInfo={foursquareContact}></GenericContact>
                    </div>
                );
            });
        }
        return (
            <div className="list-group">
                {allFoursquareContacts}
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
    postal_code : React.PropTypes.string,
    contact_no : React.PropTypes.string,
    // industry : React.PropTypes.string,
    fan_count : React.PropTypes.number,
    hours : React.PropTypes.string,
    link : React.PropTypes.string,
    longitude : React.PropTypes.string,
    latitude : React.PropTypes.string
}
