import React from "react";
import 'whatwg-fetch'; // safari does not have "fetch" function -> http://stackoverflow.com/questions/35830202/fetch-not-defined-in-safari-referenceerror-cant-find-variable-fetch

const TIMEOUT = 1000

export class Input extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            inputValue: '',
            inputTime: null
        };
    }

    queryBackend(event) {
        this.setState({inputTime: Date.now()})
        var currentInput = event.target.value + "";
        this.setState({inputValue: currentInput});
        if (currentInput == ""){
            this.setState({inputValue: currentInput});
            this.props.setSettingsHandler({});
            return
        }
        setTimeout(function() {
            if (this.state.inputTime == null || Date.now() - this.state.inputTime < TIMEOUT){
                console.log("Waiting for keystrokes")
                return
            }
            var component = this; //required in promise
            component.props.setLastQueryHandler(currentInput);
            fetch('https://backend.crawlz.me/api/fastSearch/' + currentInput, {
              method: 'GET',
              headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
              }
            }).then(function(response) {
                response.json().then(function(json) {
                    component.props.setSettingsHandler(json, currentInput);
                });
            });
            
        }.bind(this), TIMEOUT);

    }

    keyUp(event){
        if (event.key == 'Enter'){
            var component = this; //required in promise
            if (event.target.value == ""){
                this.setState({inputValue: event.target.value});
                component.props.setSettingsHandler({});
                return
            }
            var locationTrailer = ""
            if (localStorage.lat && localStorage.lon){
                locationTrailer = locationTrailer + "?lat=" + String(localStorage.lat) + "&lon=" + String(localStorage.lon)
            }
            fetch('https://backend.crawlz.me/api/search/' + event.target.value + locationTrailer, {
              method: 'GET',
              headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
              }
            }).then(function(response) {
                response.json().then(function(json) {
                    component.props.setSettingsHandler(json);
                });
            });
        }
    }

    render() {
        return (
            <div className="col-xs-12 form-group row">
                <input className="form-control" value={this.state.inputValue} type="search" 
                    onChange={this.queryBackend.bind(this)}
                    onKeyDown={this.keyUp.bind(this)} 
                    id="searchInput" rows="1" placeholder="Search for..">
                </input>
            </div>
        );
    }
}