import React from "react";
import { GenericContact } from "./GenericContact";

export class FacebookContact extends React.Component {
    constructor(props) {
        super(props);
    } 

    render() {
        var allFacebookContacts = []
        if (this.props.facebookContacts != null){
            allFacebookContacts = this.props.facebookContacts.map((facebookContact) => {
                return (
                    <div key={facebookContact.facebook_resource_locator}>
                        <GenericContact contactInfo={facebookContact}></GenericContact>
                    </div>
                );
            });
        }
        return (
            <div className="list-group">
                {allFacebookContacts}
            </div>
        );
    }
}

FacebookContact.propTypes = {
    facebook_resource_locator : React.PropTypes.string,
    org_name : React.PropTypes.string,
    description : React.PropTypes.string,
    address : React.PropTypes.string,
    country : React.PropTypes.string,
    state : React.PropTypes.string,
    postal_code : React.PropTypes.number,
    contact_no : React.PropTypes.string,
    industry : React.PropTypes.string,
    fan_count : React.PropTypes.number,
    hours : React.PropTypes.string,
    link : React.PropTypes.string,
    longitude : React.PropTypes.string,
    latitude : React.PropTypes.string,
    intl_number_with_plus : React.PropTypes.string

}