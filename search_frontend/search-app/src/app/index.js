import React from 'react';
import { render } from 'react-dom';

import { Header } from "./components/Header";
import { Input } from "./components/Input";
import { Results } from "./components/Results";

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            settings: {
                facebookViewSettings : {},
                linkedinViewSettings : {},
                googleMapsViewSettings : {},
                foursquareViewSettings : {},
                commonViewSettings : {}
            },
            contacts: {
                facebookContacts : [],
                linkedinContacts : [],
                googleMapsContacts : [],
                foursquareContacts : []
            }
        };
    }
    setSettings(contacts) {
        this.setState({
            contacts: contacts
        })
        console.log(this.state.contacts)
    }
    render() {
        return (
            <div className="container">
                <div className="row">
                    <div className="col-xs-10 col-xs-offset-1">
                        <Header />
                    </div>
                </div>
                <div className="row">
                    <div className="col-xs-10 col-xs-offset-1">
                        <Input setSettingsHandler={this.setSettings.bind(this)}/>
                    </div>
                </div>
                <div className="row">
                    <div className="col-xs-10 col-xs-offset-1">
                        <Results contacts={this.state.contacts}/>
                    </div>
                </div> 
            </div>
        );
    }
}

App.propTypes = {

}

render(<App />, window.document.getElementById('app'));


