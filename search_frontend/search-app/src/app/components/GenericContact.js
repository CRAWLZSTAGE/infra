import React from "react";

export class GenericContact extends React.Component {
    constructor(props) {
        super(props);
    };
    
    render() {
        let contact_no = null;
        let description = null;
        let address = "";
        let button = null;
        if (this.props.contactInfo.contact_no || this.props.contactInfo.intl_number_with_plus){
            var contact = (this.props.contactInfo.contact_no ? this.props.contactInfo.contact_no : this.props.contactInfo.intl_number_with_plus)
            contact_no = <p>Contact Number: {contact}</p>
            button = <a href={"tel:" + contact.replace(/[()-\s]*/g, "")}><button className="btn btn-success">Call me!</button></a> 
        };
        if (this.props.contactInfo.description){
            description = <p> {this.props.contactInfo.description} </p>
        };
        if (this.props.contactInfo.address || this.props.contactInfo.country){
        	if (this.props.contactInfo.address != null){
        		address += this.props.contactInfo.address
        	}
        	if (this.props.contactInfo.postal_code != null){
                address += address != "" ? ", " + this.props.contactInfo.postal_code : this.props.contactInfo.postal_code
            }
            if (this.props.contactInfo.country != null){
                address += address != "" ? ", " + this.props.contactInfo.country : this.props.contactInfo.country
            }
            address = <p> {address} </p>
        };
        return (
            <div className="col-xs-10" key={this.props.contactInfo.facebook_resource_locator}>
                <h3>{this.props.contactInfo.org_name}</h3>
                {contact_no}
                {address}
                {description}
                {button}
            </div>
        );

    }
}

GenericContact.propTypes = {
    facebook_resource_locator : React.PropTypes.string,
    org_name : React.PropTypes.string,
    description : React.PropTypes.string,
    address : React.PropTypes.string,
    country : React.PropTypes.string,
    postal_code : React.PropTypes.number,
    contact_no : React.PropTypes.string,
    industry : React.PropTypes.string,
    intl_number_with_plus : React.PropTypes.string

}