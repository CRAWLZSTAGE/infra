import React from "react";

import { FacebookContact } from "./FacebookContact";
import { GoogleContact } from "./GoogleContact";
import { FoursquareContact } from "./FoursquareContact";

const facebookStyle = {
  "background-color": "aliceblue"
};

const googleStyle = {
  "background-color": "#BDECB6"
};

const fsquareStyle = {
  "background-color": "mistyrose"
};    

export class Results extends React.Component {
    constructor(props) {
        super(props);
    }
    render() {
        return (
            <div className="container">
                <div className="row">
                    <div className="col-xs-12" style={facebookStyle}>
                        <FacebookContact facebookContacts={this.props.contacts.facebookContacts} />
                    </div>
                </div>
                <div className="row">
                    <div className="col-xs-12" style={googleStyle}>
                        <GoogleContact googleContacts={this.props.contacts.googleContacts} />
                    </div>
                </div>
                <div className="row">
                    <div className="col-xs-12" style={fsquareStyle}>
                        <FoursquareContact foursquareContacts={this.props.contacts.foursquareContacts} />
                    </div>
                </div>
            </div>
        );
    }
}