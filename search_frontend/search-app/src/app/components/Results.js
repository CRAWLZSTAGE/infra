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
                        <GoogleContact />
                    </div>
                </div>
                <div className="row">
                    <div className="col-xs-10 col-xs-offset-1">
                        <FoursquareContact />
                    </div>
                </div>
            </div>
        );
    }
}