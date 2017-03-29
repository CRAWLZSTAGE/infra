import React from "react";
import { GenericContact } from "./GenericContact";

export class GoogleContact extends React.Component {
    constructor(props) {
        super(props);
    } 

    render() {
        var allGoogleContacts = [];
        if (this.props.googleContacts != null){
            allGoogleContacts = this.props.googleContacts.map((googleContact) => {
                return (
                    <div key={googleContact.google_resource_locator}>
                        <GenericContact contactInfo={googleContact}></GenericContact>
                    </div>
                );
            });
        }
        return (
            <div className="list-group">
                {allGoogleContacts}
            </div>
        );
    }
}

GoogleContact.propTypes = {
    google_resource_locator : React.PropTypes.string,
    org_name : React.PropTypes.string,
    address : React.PropTypes.string,
    country : React.PropTypes.string,
    postal_code : React.PropTypes.string,
    contact_no : React.PropTypes.string,
    industry : React.PropTypes.string,
    rating : React.PropTypes.number,
    link : React.PropTypes.string,
    longitude : React.PropTypes.string,
    latitude : React.PropTypes.string,
    intl_number_with_plus : React.PropTypes.string
}

