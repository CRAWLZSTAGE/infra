import React from "react";

import { FacebookContact } from "./FacebookContact";
import { GoogleContact } from "./GoogleContact";
import { FoursquareContact } from "./FoursquareContact";

const FacebookContactList = ({facebookContact}) => {
  return (
    <div>
       <div>
          <h1>MEHHH</h1>
       </div>
    </div>
  );
}

export class Results extends React.Component {
    constructor(props) {
        super(props);
    }
    render() {
        return (
            <div className="container">
                <div className="row">
                    <div className="col-xs-10 col-xs-offset-1">
                        <FacebookContact facebookContacts={this.props.contacts.facebookContacts}/>
                    </div>
                </div>
                <div className="row">
                    <div className="col-xs-10 col-xs-offset-1">
                        <GoogleContact googleContacts={this.props.contacts.googleContacts}/>
                    </div>
                </div>
                <div className="row">
                    <div className="col-xs-10 col-xs-offset-1">
                        <FoursquareContact foursquareContacts={this.props.contacts.foursquareContacts}/>
                    </div>
                </div>
            </div>
        );
    }
}