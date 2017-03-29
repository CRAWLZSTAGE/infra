import React from "react";

export class FacebookContact extends React.Component {
    constructor(props) {
        super(props);
    }

    call_me() {
        console.log("TBC")
    }

    set_contact_info(facebookContact, contact_no, description, address){

    }
    

    render() {
        var allFacebookContacts = []
        if (this.props.facebookContacts != null){
            allFacebookContacts = this.props.facebookContacts.map((facebookContact) => {
                let contact_no = null;
                let description = null;
                let address = null;
                let button = null;
                if (facebookContact.contact_no || facebookContact.intl_number_with_plus){
                    var contact = (facebookContact.contact_no ? facebookContact.contact_no : facebookContact.intl_number_with_plus)
                    contact_no = <p>Contact Number: {contact}</p>
                    button = <a href={"tel:" + contact.replace(/[()-]*\s/g, "")}><button onClick={this.call_me.bind(this)} className="btn btn-success">Call me!</button></a> 
                };
                if (facebookContact.description){
                    description = <p> {facebookContact.description} </p>
                };
                if (facebookContact.address || facebookContact.country){
                    if (facebookContact.address == null){
                        address = <p> {"" + facebookContact.country} </p>
                    }else if (facebookContact.country == null){
                        address = <p> {"" + facebookContact.address} </p>
                    }else{
                        address = <p> {"" + facebookContact.address + facebookContact.country} </p>
                    }
                    
                };
                return (
                    <div className="col-xs-8" key={facebookContact.facebook_resource_locator}>
                        <h3>{facebookContact.org_name}</h3>
                        {contact_no}
                        {description}
                        {address}
                        {button}
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