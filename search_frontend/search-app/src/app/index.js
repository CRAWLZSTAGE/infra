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
                googleContacts : [],
                foursquareContacts : []
            },
            lastQuery: ""
        };
    }
    setLastQuery(currentQuery) {
        this.setState({
            lastQuery: currentQuery
        })
        console.log("CurrentQuery: " + this.state.lastQuery)
    }
    setSettings(contacts, currentQuery) {
        if (this.state.lastQuery == currentQuery){
            this.setState({
                contacts: contacts
            })
            console.log(this.state.contacts)
        }else{
            console.log("CurrentQuery: " + currentQuery + " does not match lastQuery: " + this.state.lastQuery)
        }
    }
    render() {
        return (
            <div className="container">
                <div className="row">
                    <div className="col-xs-12">
                        <Header />
                    </div>
                </div>
                <div className="row">
                    <div className="col-xs-12">
                        <Input setSettingsHandler={this.setSettings.bind(this)} setLastQueryHandler={this.setLastQuery.bind(this)}/>
                    </div>
                </div>
                <div className="row">
                    <div className="col-xs-12">
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


